from marshmallow import Schema as Schema_
from marshmallow_dataclass import dataclass as ma_dataclass
from dataclasses import field
from datetime import datetime
from typing import ClassVar, Type, Optional, List, Any, Union
import enum


class EnumMixin:
    @classmethod
    def options(cls) -> List[Any]:
        return [o.value for o in cls]  # type: ignore

    def __str__(self) -> Any:
        return self.value  # type: ignore


class Granularity(EnumMixin, enum.Enum):
    PATIENT = "patient"
    EVENT = "event"
    OTHER = "other"


class AnalyticDatasetStatus(EnumMixin, enum.Enum):
    NOT_STARTED = "notStarted"
    IN_PROGRESS = "inProgress"
    COMPRESSING = "compressing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalyticDatasetFormat(EnumMixin, enum.Enum):
    PARQUET = "parquet"
    CSV = "csv"
    ZIP = "zip"
    MULTIPARTPARQUETZIP = "MULTIPARTPARQUETZIP"


class AnalyticDatasetSource(EnumMixin, enum.Enum):
    STANDARD = "standard"
    UPLOAD = "upload"


class JoinType(EnumMixin, enum.IntEnum):
    INNER = 1
    LEFT_OUTER = 2
    RIGHT_OUTER = 3


class ColumnSelectionType(EnumMixin, enum.IntEnum):
    ALL = 1
    CUSTOM = 2


@ma_dataclass
class AnalyticDatasetModel:
    definition_id: Optional[str] = field(metadata=dict(data_key="analyticDatasetDefinitionId"), default=None)
    asset_id: Optional[str] = field(metadata=dict(data_key="assetId"), default=None)
    dataset_release_identifier: Optional[str] = field(metadata=dict(data_key="datasetReleaseIdentifier"), default=None)
    cohort_of_interest_asset_id: Optional[str] = field(metadata=dict(data_key="cohortOfInterestAssetId"), default=None)
    created_by: Optional[str] = field(metadata=dict(data_key="createdByUserId"), default=None)
    combine_events_on_same_day: Optional[bool] = field(metadata=dict(data_key="combineEventsOnSameDay"), default=None)
    cohort_of_interest: int = field(metadata=dict(data_key="cohortOfInterestId"), default=0)
    granularity: Granularity = field(metadata=dict(by_value=True), default=Granularity.PATIENT)
    status: AnalyticDatasetStatus = field(metadata=dict(by_value=True), default=AnalyticDatasetStatus.NOT_STARTED)
    source: AnalyticDatasetSource = field(metadata=dict(by_value=True), default=AnalyticDatasetSource.STANDARD)
    output_type: AnalyticDatasetFormat = field(metadata=dict(by_value=True, data_key="outputType"), default=AnalyticDatasetFormat.CSV)
    generate_asset: bool = field(metadata=dict(by_value=True, data_key="generateAsset"), default=True)
    result: dict = field(default_factory=dict)
    id: str = ""
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    Schema: ClassVar[Type[Schema_]] = Schema_  # needed for type checking


@ma_dataclass
class AnalyticDatasetDefinitionModel:
    dataset_schema_id: str = field(metadata=dict(data_key="datasetSchemaId"), default="")
    created_by_user_id: str = field(metadata=dict(data_key="createdByUserId"), default="")
    original_cohort_id: Optional[int] = field(metadata=dict(data_key="originalCohortId"), default=None)
    original_cohort_asset_id: str = field(metadata=dict(data_key="originalCohortAssetId"), default="")
    study_period_from: Optional[datetime] = field(metadata=dict(data_key="studyPeriodFrom"), default=None)
    study_period_to: Optional[datetime] = field(metadata=dict(data_key="studyPeriodTo"), default=None)
    container_id: str = field(metadata=dict(data_key="containerId"), default="")
    asset_id: str = field(metadata=dict(data_key="workspaceAssetId"), default="")
    patient_count: int = field(metadata=dict(data_key="patientCount"), default=0)
    characteristics: list = field(default_factory=list)
    demographic_characteristics: Optional[list] = field(metadata=dict(data_key="demographicCharacteristics"), default=None)
    rights: dict = field(default_factory=dict)
    capabilities: dict = field(default_factory=dict)
    cohort_of_interest_indexdate_type: Optional[Union[int, str]] = field(metadata=dict(data_key="cohortOfInterestIndexDateType"), default=None)  # TODO: make an Enum
    source: AnalyticDatasetSource = field(metadata=dict(by_value=True), default=AnalyticDatasetSource.STANDARD)
    default_granularity: Granularity = field(metadata=dict(by_value=True, data_key="defaultGranularity"), default=Granularity.PATIENT)
    asset_name: Optional[str] = field(metadata=dict(data_key="assetName"), default=None)
    is_asset_hidden: Optional[bool] = field(metadata=dict(data_key="isAssetHidden"), default=None)
    is_error_loading: Optional[bool] = field(metadata=dict(data_key="isErrorLoading"), default=None)
    high_dimensional_characteristics: Optional[list] = field(metadata=dict(data_key="highDimensionalCharacteristics"), default=None)
    analytic_dataset_merge_characteristics: Optional[list] = field(metadata=dict(data_key="analyticDatasetMergeCharacteristics"), default=None)
    cohort_asset_options: Optional[dict] = field(metadata=dict(data_key="cohortAssetOptions"), default=None)
    id: str = ""
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    Schema: ClassVar[Type[Schema_]] = Schema_  # needed for type checking


@ma_dataclass
class AnalyticDatasetMergeRequestModel:
    dataset_asset_id: Optional[str] = field(default=None, metadata=dict(data_key='analyticDatasetAssetId'))
    source_join_column: Optional[str] = field(default=None, metadata=dict(data_key='sourceJoinColumn'))
    dest_join_column: Optional[str] = field(default=None, metadata=dict(data_key='destJoinColumn'))
    join_type: JoinType = field(default=JoinType.LEFT_OUTER, metadata=dict(by_value=True, data_key='joinType'))
    column_selection_type: ColumnSelectionType = field(metadata=dict(by_value=True, data_key='columnSelectionType'), default=ColumnSelectionType.ALL)
    selected_columns: List[str] = field(default_factory=list, metadata=dict(data_key='selectedColumns'))
    Schema: ClassVar[Type[Schema_]] = Schema_  # needed for type checking

    def __post_init__(self) -> None:
        if self.column_selection_type == ColumnSelectionType.CUSTOM:
            if not self.selected_columns:
                raise ValueError('When column_selection_type is CUSTOM, the selected_columns must also be provided.')
