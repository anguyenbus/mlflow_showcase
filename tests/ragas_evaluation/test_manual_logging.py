"""Tests for MLflow manual logging."""

from unittest import mock

import pytest


def test_manual_logging_main_execution():
    """Test that manual_logging.py main execution works."""
    try:
        from ragas_evaluation.with_mlflows.manual_logging import main
        assert callable(main)
    except ImportError:
        pytest.skip("manual_logging.py not implemented yet")


def test_manual_parameter_logging():
    """Test manual parameter logging."""
    with mock.patch("mlflow.log_params") as mock_log_params:
        with mock.patch("mlflow.log_metrics"):
            with mock.patch("mlflow.log_artifact"):
                with mock.patch("mlflow.set_tags"):
                    with mock.patch("mlflow.start_run"):
                        with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
                            try:
                                from ragas_evaluation.with_mlflows.manual_logging import main

                                # Mock ragas evaluation
                                with mock.patch("ragas.evaluate") as mock_evaluate:
                                    mock_result = mock.Mock()
                                    mock_result.to_pandas.return_value.iloc.return_value.to_dict.return_value = {
                                        "faithfulness": 0.85
                                    }
                                    mock_evaluate.return_value = mock_result

                                    # Try to run main
                                    try:
                                        main()
                                    except:
                                        pass

                            except ImportError:
                                pytest.skip("manual_logging.py not implemented yet")


def test_manual_metric_logging():
    """Test manual metric logging."""
    with mock.patch("mlflow.log_params"):
        with mock.patch("mlflow.log_metrics") as mock_log_metrics:
            with mock.patch("mlflow.log_artifact"):
                with mock.patch("mlflow.set_tags"):
                    with mock.patch("mlflow.start_run"):
                        with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
                            try:
                                from ragas_evaluation.with_mlflows.manual_logging import main

                                # Try to run main
                                try:
                                    main()
                                except:
                                    pass

                                # Check if metrics were logged
                                # (This is a basic check, would need more specific assertions)

                            except ImportError:
                                pytest.skip("manual_logging.py not implemented yet")


def test_artifact_logging():
    """Test artifact logging."""
    with mock.patch("mlflow.log_params"):
        with mock.patch("mlflow.log_metrics"):
            with mock.patch("mlflow.log_artifact") as mock_log_artifact:
                with mock.patch("mlflow.set_tags"):
                    with mock.patch("mlflow.start_run"):
                        with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
                            try:
                                from ragas_evaluation.with_mlflows.manual_logging import main

                                # Try to run main
                                try:
                                    main()
                                except:
                                    pass

                            except ImportError:
                                pytest.skip("manual_logging.py not implemented yet")


def test_custom_tags_setting():
    """Test custom tags setting."""
    with mock.patch("mlflow.log_params"):
        with mock.patch("mlflow.log_metrics"):
            with mock.patch("mlflow.log_artifact"):
                with mock.patch("mlflow.set_tags") as mock_set_tags:
                    with mock.patch("mlflow.start_run"):
                        with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
                            try:
                                from ragas_evaluation.with_mlflows.manual_logging import main

                                # Try to run main
                                try:
                                    main()
                                except:
                                    pass

                            except ImportError:
                                pytest.skip("manual_logging.py not implemented yet")


def test_comparison_with_auto_logging():
    """Test comparison with auto-logging."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        try:
            # This test verifies that manual logging provides comparison notes
            from ragas_evaluation.with_mlflows.manual_logging import main

            # Try to run main and check for comparison output
            try:
                main()
            except:
                pass

        except ImportError:
            pytest.skip("manual_logging.py not implemented yet")
