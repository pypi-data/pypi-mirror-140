// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Sets the logging callback for the application.
 *
 * @in-param MSALRUNTIME_LOG_CALLBACK_ROUTINE callback - logging callback function. Must be a valid function.
 *
 * @return - null handle, success, otherwise fail.
 */
MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_API
MSALRUNTIME_SetLoggingCallback(MSALRUNTIME_LOG_CALLBACK_ROUTINE callback, void* callbackData);

/*
 * Gets the logEntry string associated with the logEntry handle.
 *
 * @in-param MSALRUNTIME_LOG_ENTRY_HANDLE logEntryHandle - the logEntry handle.
 * @out-param os_char* logEntry - the buffer that is used to copy the logEntry into.
 * @in-out-param int32_t* bufferSize - this parameter contains the size of the buffer (number of characters +
 * null terminator) and is updated by the method to indicate the actual size of the buffer.
 * @out-param MSALRUNTIME_LOG_LEVEL* logLevel the logLevel that is associated with the logEntry.
 *
 * @return - null handle, success.
 * Handle with InsufficientBuffer status, if the buffer is too small, then bufferSize contains the new size to be
 * allocated. Otherwise fail.
 */
MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_API MSALRUNTIME_GetLogEntry(
    MSALRUNTIME_LOG_ENTRY_HANDLE logEntryHandle,
    os_char* logEntry,
    int32_t* bufferSize,
    MSALRUNTIME_LOG_LEVEL* logLevel);

/*
 * Releases the allocated MSALRUNTIME_ERROR_HANDLE in the MSALRuntime.
 *
 * @in-param MSALRUNTIME_ERROR_HANDLE error - the error handle.
 *
 * @return - success if null handle, otherwise fail.
 */
MSALRUNTIME_ERROR_HANDLE MSALRUNTIME_API MSALRUNTIME_ReleaseLogEntry(MSALRUNTIME_LOG_ENTRY_HANDLE logEntryHandle);

#ifdef __cplusplus
}
#endif
