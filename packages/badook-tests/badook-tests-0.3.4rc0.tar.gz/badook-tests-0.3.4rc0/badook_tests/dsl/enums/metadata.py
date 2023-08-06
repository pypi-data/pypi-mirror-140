from enum import Enum


class MetadataColumn(Enum):
    NUM_OF_ROWS_COLUMN = 'num_rows'
    NUM_OF_DUPLICATES_COLUMN = 'num_duplicates'
    NUM_OF_MISSING_VALUES_COLUMN = 'num_missing'
    NUM_OF_INVALID_TYPE_COLUMN = 'num_invalid_type'
