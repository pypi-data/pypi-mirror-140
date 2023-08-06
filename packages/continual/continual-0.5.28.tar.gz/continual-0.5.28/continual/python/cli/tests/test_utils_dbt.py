import unittest
import tempfile
import os

from continual.python.cli import utils_dbt


class process_dbt_project_file(unittest.TestCase):
    def test_should_parse_dbt_project_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dbt_project_file_path = os.path.join(tmpdir, "dbt_project.yml")
            with open(dbt_project_file_path, "w+") as dbt_project_file:
                dbt_project_file.writelines(
                    """
name: 'my_new_project'
version: '1.0.0'
config-version: 2

profile: 'default'

model-paths: ["models"]
analysis-paths: ["analysis"]
test-paths: ["tests"]
seed-paths: ["data"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_modules"

models:
  my_new_project:                
                """
                )

            (
                dbt_project_config_file_path,
                dbt_project_name,
                dbt_default_profile_name,
                dbt_target_dir,
                dbt_manifest_file_path,
            ) = utils_dbt.process_dbt_project_file(tmpdir)

            assert dbt_project_config_file_path == os.path.join(
                tmpdir, "dbt_project.yml"
            )
            assert dbt_project_name == "my_new_project"
            assert dbt_default_profile_name == "default"
            assert dbt_target_dir == "target"
            assert dbt_manifest_file_path == os.path.join(
                tmpdir, "target/manifest.json"
            )


class get_default_target(unittest.TestCase):
    def test_should_get_profile_target_name(self):
        dbt_profiles_file_path = ""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbt_profiles_file_path = os.path.join(tmpdir, "profiles.yml")
            with open(dbt_profiles_file_path, "w+") as dbt_profiles_file:
                dbt_profiles_file.writelines(
                    """
a_profile_name:
  outputs:
    a_target_name:
      type: snowflake
      account: a_snowflake_account
      user: a_snowflake_user
      password: a_snowflake_password
      role: a_snowflake_role
      database: a_snowflake_database
      warehouse: a_snowflake_warehouse
      schema: a_snowflake_schema_name

  target: a_target_name            
                """
                )

            result = utils_dbt.get_default_target(
                dbt_profiles_file_path, "a_profile_name"
            )
            assert result == "a_target_name"

    def test_should_handle_case_sensitive_profile_names(self):
        dbt_profiles_file_path = ""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbt_profiles_file_path = os.path.join(tmpdir, "profiles.yml")
            with open(dbt_profiles_file_path, "w+") as dbt_profiles_file:
                dbt_profiles_file.writelines(
                    """
A_Profile_Name_With_Capital_Letters:
  outputs:
    a_target_name:
      type: snowflake
      account: a_snowflake_account
      user: a_snowflake_user
      password: a_snowflake_password
      role: a_snowflake_role
      database: a_snowflake_database
      warehouse: a_snowflake_warehouse
      schema: a_snowflake_schema_name

  target: a_target_name
                """
                )

            result = utils_dbt.get_default_target(
                dbt_profiles_file_path, "A_Profile_Name_With_Capital_Letters"
            )
            assert result == "a_target_name"

    def test_should_handle_case_sensitive_keys(self):
        dbt_profiles_file_path = ""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbt_profiles_file_path = os.path.join(tmpdir, "profiles.yml")
            with open(dbt_profiles_file_path, "w+") as dbt_profiles_file:
                dbt_profiles_file.writelines(
                    """
a_profile_name:
  outputs:
    a_target_name:
      type: snowflake
      account: a_snowflake_account
      user: a_snowflake_user
      password: a_snowflake_password
      role: a_snowflake_role
      database: a_snowflake_database
      warehouse: a_snowflake_warehouse
      schema: a_snowflake_schema_name

  TARGET: a_target_name     
                """
                )

            result = utils_dbt.get_default_target(
                dbt_profiles_file_path, "a_profile_name"
            )
            # dbt requires keys to be lowercase: https://linear.app/continual/issue/DEV-2805/dbt-profile-config-keys-are-case-sensitive
            assert result is None
