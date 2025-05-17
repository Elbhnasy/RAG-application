from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS = "file_validate_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    FILE_PROCESSING_SUCCESS = "file_processing_success"
    FILE_PROCESSING_FAILED = "file_processing_failed"
    NO_FILES_ERROR = "file_not_found"
    FILE_ID_ERROR = "no_file_found_with_this_id"
    