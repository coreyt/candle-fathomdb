"""Exercise action selection/binding only; synthetic owner labels grant nothing."""
import hashlib
import json
import os
import pathlib
import tempfile
import time
import unittest
from unittest.mock import patch
import campaign


class Campaign(unittest.TestCase):
    def test_healthy_default_needs_no_fault_action(self):
        with patch.dict(os.environ, {}, clear=True):
            mode, arms, _ = campaign.configuration()
            self.assertEqual((mode, arms), ('healthy', ['a', 'b']))
            self.assertIsNone(campaign.ACTION)

    def test_fault_needs_owner_label_action_and_shared_clock(self):
        with patch.dict(os.environ, {'FATHOMDB_COORDINATED_CAMPAIGN':'reset-drop','FATHOMDB_ARTIFACT_ARMS':'final'}, clear=True):
            with self.assertRaises(RuntimeError): campaign.configuration()

    def test_immutable_case_and_venue_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            action = {'venue': {'action':'slice60-process-primary-v1','host':'windchill3','arch':'x86_64','uuid':'GPU-5f9cfc90-2be1-06a7-ce39-5a6d294b209b','resource_rule':'original','visibility_rule':'nvml-compute-graphics','lock':str(root/'lease'),'lock_inode':123},'cases':{'one':{'argv':['/owned/binary','--exact','selected'],'executable_sha256':'a'*64}}}
            payload = json.dumps(action).encode(); path=root/'action.json';path.write_bytes(payload)
            env={'SLICE60_ROOT':directory,'FATHOMDB_COORDINATED_CAMPAIGN':'reset-drop','FATHOMDB_ARTIFACT_ARMS':'final','FATHOMDB_RESET_AUTHORIZATION':'seq-999','FATHOMDB_RESET_ACTION':'slice60-process-primary-v1','FATHOMDB_VENUE_STARTED_MONOTONIC':str(time.monotonic()),'FATHOMDB_GPU_UUID':action['venue']['uuid'],'FATHOMDB_GPU_LOCK':str(root/'lease'),'FATHOMDB_GPU_LOCK_INODE':'123','FATHOMDB_RESET_ACTION_FILE':str(path),'FATHOMDB_RESET_ACTION_SHA256':hashlib.sha256(payload).hexdigest()}
            with patch.dict(os.environ,env,clear=True),patch('campaign.platform.node',return_value='windchill3'),patch('campaign.platform.machine',return_value='x86_64'):
                campaign.configuration();campaign.bind_case('one',action['cases']['one'])
                with self.assertRaises(RuntimeError):campaign.bind_case('one',dict(action['cases']['one'],argv=['/different/binary']))
                with patch.dict(os.environ,{'FATHOMDB_RESET_ACTION_SHA256':'0'*64}):
                    with self.assertRaises(RuntimeError):campaign.configuration()
                with patch.dict(os.environ,{'FATHOMDB_GPU_UUID':'GPU-wrong'}):
                    with self.assertRaises(RuntimeError):campaign.configuration()
                with patch.dict(os.environ,{'FATHOMDB_FAULT_RESOURCE_RULE':'r580-ram40-24-swap-report','FATHOMDB_GPU_UUID':'GPU-wrong'}):
                    with self.assertRaises(RuntimeError):campaign.configuration()


if __name__=='__main__':unittest.main()
