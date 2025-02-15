import xmlrpc
from time import sleep

import pytest

from supervisor_pydantic import SupervisorConvenienceConfiguration, SupervisorRemoteXMLRPCClient
from supervisor_pydantic.client.xmlrpc import ProcessState


def _assert_client_actions(client: SupervisorRemoteXMLRPCClient, name: str = "test"):
    assert client.getProcessInfo(name).state == ProcessState.STOPPED
    sleep(1)
    assert client.startAllProcesses()[name].state == ProcessState.RUNNING
    sleep(1)
    assert client.getProcessInfo(name).state == ProcessState.EXITED
    assert client.startProcess(name).state == ProcessState.RUNNING
    assert client.stopProcess(name).state == ProcessState.STOPPED
    assert client.startProcess(name).state == ProcessState.RUNNING
    assert client.stopAllProcesses()[name].state == ProcessState.STOPPED


def test_supervisor_client(supervisor_instance: SupervisorConvenienceConfiguration):
    client = SupervisorRemoteXMLRPCClient(supervisor_instance)
    _assert_client_actions(client=client)


def test_supervisor_client_changes(supervisor_instance: SupervisorConvenienceConfiguration):
    client = SupervisorRemoteXMLRPCClient(supervisor_instance)
    _assert_client_actions(client=client)
    test_program = supervisor_instance.program.pop("test")
    supervisor_instance.program["test2"] = test_program
    supervisor_instance._write_self()
    client = SupervisorRemoteXMLRPCClient(supervisor_instance)
    client.reloadConfig()
    print(supervisor_instance)
    _assert_client_actions(client=client, name="test2")


def test_permissioned_supervisor_client_rejected(permissioned_supervisor_instance: SupervisorConvenienceConfiguration):
    permissioned_supervisor_instance.convenience.username = "bad-username"
    client = SupervisorRemoteXMLRPCClient(permissioned_supervisor_instance)
    with pytest.raises(xmlrpc.client.ProtocolError):
        client.getProcessInfo("test")


def test_permissioned_supervisor_client(permissioned_supervisor_instance: SupervisorConvenienceConfiguration):
    permissioned_supervisor_instance.convenience.username = "user1"
    client = SupervisorRemoteXMLRPCClient(permissioned_supervisor_instance)
    _assert_client_actions(client=client)
