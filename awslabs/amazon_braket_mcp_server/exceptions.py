# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Exception classes for Amazon Braket MCP Server."""


class BraketMCPException(Exception):
    """Base exception class for Amazon Braket MCP Server."""

    pass


class CircuitCreationError(BraketMCPException):
    """Exception raised when there is an error creating a quantum circuit."""

    pass


class TaskExecutionError(BraketMCPException):
    """Exception raised when there is an error executing a quantum task."""

    pass


class TaskResultError(BraketMCPException):
    """Exception raised when there is an error retrieving task results."""

    pass


class DeviceError(BraketMCPException):
    """Exception raised when there is an error with a quantum device."""

    pass


class VisualizationError(BraketMCPException):
    """Exception raised when there is an error visualizing a circuit or results."""

    pass
