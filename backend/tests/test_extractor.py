import json
import os
import unittest
from unittest.mock import patch

from services import extractor


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


class ExtractorIntegrationTests(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "MODEL_BASE_URL": "http://localhost:8080/v1",
            "MODEL_NAME": "order-extractor",
        },
        clear=False,
    )
    @patch("urllib.request.urlopen")
    def test_llama_response_is_normalized_to_backend_contract(self, urlopen):
        urlopen.return_value = _FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": (
                                "```json\n"
                                '{"origin":"Ambon","destination":"Surabaya",'
                                '"commodity":"tuna","weight_kg":300,'
                                '"temperature_min_c":0,"temperature_max_c":4,'
                                '"pickup_deadline":"besok pagi"}\n'
                                "```"
                            )
                        }
                    }
                ]
            }
        )

        result = extractor.extract_order("300 kg tuna Ambon ke Surabaya")

        self.assertEqual(result["details"]["origin"], "Ambon")
        self.assertEqual(result["details"]["destination"], "Surabaya")
        self.assertEqual(result["details"]["cargo_type"], "tuna")
        self.assertEqual(result["details"]["weight"], 300)
        self.assertEqual(result["details"]["unit"], "kg")
        self.assertEqual(result["details"]["temp_requirement"], "0_4")
        self.assertEqual(result["details"]["delivery_time"], "besok pagi")

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://localhost:8080/v1/chat/completions")
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "order-extractor")
        self.assertEqual(body["response_format"], {"type": "json_object"})

    @patch.dict(
        os.environ,
        {"MODEL_BASE_URL": "http://localhost:8080/v1"},
        clear=False,
    )
    @patch("urllib.request.urlopen")
    def test_invalid_model_json_raises_runtime_error(self, urlopen):
        urlopen.return_value = _FakeResponse(
            {
                "choices": [{"message": {"content": "not valid json"}}]
            }
        )

        with self.assertRaises(RuntimeError):
            extractor.extract_order("order tanpa format jelas")

    def test_negative_temperature_range_is_converted_to_order_fields(self):
        fields = extractor.inference_to_order_fields(
            {"details": {"temp_requirement": "-20_-18"}}
        )

        self.assertEqual(fields["temperature_min_c"], -20.0)
        self.assertEqual(fields["temperature_max_c"], -18.0)


if __name__ == "__main__":
    unittest.main()
