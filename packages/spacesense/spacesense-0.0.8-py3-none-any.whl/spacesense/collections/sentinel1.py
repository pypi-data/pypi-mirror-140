import datetime
import logging
import os
import uuid
from typing import Any, List, Union

import grpc
import pandas as pd
import xarray as xr
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct
from pandas.core.frame import DataFrame
from rasterio.io import MemoryFile
from xarray.core.dataset import Dataset

from spacesense import config
from spacesense.common.proto.sentinel1 import sentinel1_pb2, sentinel1_pb2_grpc

logger = logging.getLogger(__name__)


class GrpcAuth(grpc.AuthMetadataPlugin):
    def __init__(self, key):
        self._key = key

    def __call__(self, context, callback):
        callback((("rpc-auth-header", self._key),), None)


class Sentinel1Result:
    def __init__(self):
        self.items = []
        self._dataset = None
        self._status = None

    @property
    def status(self) -> DataFrame:
        if self._status is None:
            self._compute_status()
        return self._status

    @property
    def dataset(self) -> Dataset:
        if not self._dataset:
            self._compute_dataset()
        return self._dataset

    def _compute_dataset(self):
        self._dataset = xr.concat([item.data for item in self.items], dim="time")

    def _compute_status(self):
        self._status = pd.DataFrame.from_dict([item.get_processing_status() for item in self.items], orient="columns")

    def get_scene_metadata(self, as_dataframe=False) -> Union[pd.DataFrame, List[dict]]:
        scene_metadata_with_date = []
        for item in self.items:
            date_metadata = item.scene_metadata
            for scene_metadata in date_metadata:
                scene_metadata_copy = {"date": item.date}
                scene_metadata_copy.update(scene_metadata)
                scene_metadata_with_date.append(scene_metadata_copy)
        if as_dataframe:
            return pd.DataFrame.from_dict(scene_metadata_with_date, orient="columns")
        else:
            return scene_metadata_with_date


class Sentinel1ResultItem:
    def __init__(self, date, status, scene_metadata, data=None, reason=None, file_path=None, bucket_path=None):
        self.date = date
        self.status = status
        self.scene_metadata = scene_metadata
        self.scene_ids = [one_scene_metadata["title"] for one_scene_metadata in self.scene_metadata]
        self._data = data
        self.file_path = file_path
        self.reason = reason
        self.bucket_path = bucket_path
        self.data = None
        if self.file_path:
            self.data_array = xr.open_rasterio(self.file_path)
            self.data = self._redesign_dataset(self.data_array)
        elif self._data and len(self._data) > 0:
            with MemoryFile(self._data) as mem_file:
                self.data_array = xr.open_rasterio(mem_file.name)
                self.data = self._redesign_dataset(self.data_array)

    def _redesign_dataset(self, ds):
        # reformat the metadata from the geotiff to a dict
        ds.attrs["scene_metadata"] = list(eval(ds.attrs["scene_metadata"]))
        return xr.Dataset(
            data_vars=dict(
                vh=(["y", "x"], ds[0].values),
                vv=(["y", "x"], ds[1].values),
                lia=(["y", "x"], ds[2].values),
                mask=(["y", "x"], ds[3].values),
            ),
            # TODO extract the date from the geotiff (offline mode)
            coords=dict(y=ds.y, x=ds.x, time=datetime.datetime.strptime(self.date, "%Y-%m-%d")),
            attrs=ds.attrs,
        )

    def __str__(self):
        return f"date={self.date}, status={self.status}, product_name={self.scene_ids}, data={len(self.data)}, file_path={self.file_path}"

    def get_scene_metadata(self) -> List[dict]:
        scene_metadata_with_date = []
        temp_metadata = self.scene_metadata
        for t in temp_metadata:
            scene_metadatum = t.copy()
            scene_metadatum["date"] = self.date
            scene_metadata_with_date.append(scene_metadatum)
        return scene_metadata_with_date

    def get_processing_status(self):
        return {
            "date": self.date,
            "status": self.status,
            "reason": self.reason,
            "file_path": self.file_path,
        }


class Sentinel1:
    def __init__(self, id=None, backend_url=None):
        if not backend_url:
            self.backend_url = config.BACKEND_URL
        self.api_key = os.environ.get("SS_API_KEY")
        if not self.api_key:
            raise ValueError("Could not find Spacesense API in SS_API_KEY environment variable.")
        self.id = str(uuid.uuid4()) if not id else id
        self.local_output_path = "./generated"
        self.save_to_local = False
        self.save_to_bucket = False
        self.output_crs = 4326
        self.output_resolution = 10

    def set_output_crs(self, output_crs):
        self.output_crs = output_crs

    def set_output_resolution(self, resolution):
        self.output_resolution = resolution

    def enable_bucket_output(self, bucket_output_path):
        self.save_to_bucket = True
        self.bucket_output_path = bucket_output_path

    def disable_bucket_output(self):
        self.save_to_bucket = False

    def enable_local_output(self, local_output_path="./generated"):
        self.save_to_local = True
        self.local_output_path = local_output_path

    def disable_local_output(self):
        self.save_to_local = False

    # Synchronous version
    def compute_ard(
        self,
        aoi: Any,
        start_date: Union[str, datetime.date],
        end_date: Union[str, datetime.date],
        data_coverage=100,
        mosaic=True,
    ) -> Sentinel1Result:

        aoi_param = Struct()
        aoi_param.update(aoi)

        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

        if type(start_date) != datetime.date:
            raise ValueError("Invalid start_date, should be a datetime.date object or a str in isoformat")

        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        if type(end_date) != datetime.date:
            raise ValueError("Invalid end_date, should be a datetime.date object or a str in isoformat")

        if start_date == end_date:
            end_date = end_date + datetime.timedelta(days=1)
            logger.warning("start_date and end_date are the same, adding 1 day to end_date")

        filtering_options = Struct()
        filtering_options.update({"data_coverage": data_coverage})

        output_options = Struct()
        output_options.update(
            {
                "save_to_bucket": False,
                "save_to_file": False,
                "crs": self.output_crs,
                "resolution": self.output_resolution,
            }
        )

        # Allow to transfer up to 500mo as grpc message
        channel_opt = [
            ("grpc.max_send_message_length", config.GRPC_MAX_SEND_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", config.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ]
        # with grpc.insecure_channel(config.BACKEND_URL, options=channel_opt,) as channel:
        with grpc.secure_channel(
            self.backend_url,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(config.CERT), grpc.metadata_call_credentials(GrpcAuth(self.api_key))
            ),
            options=channel_opt,
        ) as channel:
            stub = sentinel1_pb2_grpc.Sentinel1BackendStub(channel)
            responses = stub.GetS1ARD(
                sentinel1_pb2.GetS1ArdRequest(
                    id=self.id,
                    aoi=aoi_param,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    filtering_options=filtering_options,
                    output_options=output_options,
                )
            )

            s1_results = Sentinel1Result()
            for response in responses:
                scene_list = create_scene_list_object(response.scenes)
                logger.info(
                    f"date={response.date}, status={response.status}, scenes={response.scenes}, reason={response.reason}"
                )
                if response.status == "success":
                    if self.save_to_local:
                        output_dir = os.path.join(self.local_output_path, response.id)
                        file_path = os.path.join(output_dir, f"{response.date}.tiff")
                        os.makedirs(output_dir, exist_ok=True)
                        with open(file_path, "wb") as file:
                            file.write(response.data)
                        result = Sentinel1ResultItem(
                            response.date, response.status, scene_list, response.data, file_path=file_path
                        )
                    else:
                        result = Sentinel1ResultItem(response.date, response.status, scene_list)
                else:
                    result = Sentinel1ResultItem(
                        response.date,
                        response.status,
                        scene_list,
                        file_path=None,
                        reason=response.reason,
                    )
                s1_results.items.append(result)
            return s1_results

    @staticmethod
    def load_ard_from_local(id, root_dir="./generated"):
        s1_results = Sentinel1Result()
        work_dir = os.path.join(root_dir, id)
        if not id:
            raise ValueError("id is required")
        if not os.path.isdir(work_dir):
            raise ValueError(f"Previous computation result with id {id} could not found ({work_dir})")
        for filename in os.listdir(work_dir):
            file_path = os.path.join(work_dir, filename)
            # TODO: get date from the geotiff directly inside Sentinel1ResultItem
            date = filename.split(".")[0]
            result = Sentinel1ResultItem(date, "success", [], None, file_path=file_path)
            s1_results.items.append(result)
        return s1_results


def create_scene_list_object(scene_list_message: Struct) -> list:
    """
    Create a Sentinel1SceneList object from a protobuf message
    """
    return list(json_format.MessageToDict(scene_list_message).values())
