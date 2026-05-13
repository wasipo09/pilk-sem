import copy
import unittest

from model_catalog import get_model_config, list_models


class ModelCatalogTests(unittest.TestCase):
    def test_catalog_lists_known_templates(self):
        models = list_models()

        self.assertIn("utaut", models)
        self.assertIn("tpb", models)
        self.assertIn("tam2", models)
        self.assertTrue(all(description for description in models.values()))

    def test_known_templates_have_required_shape(self):
        for model_name in list_models():
            with self.subTest(model=model_name):
                config = get_model_config(model_name)

                self.assertIsInstance(config, dict)
                self.assertIsInstance(config.get("sample_size"), int)
                self.assertGreater(config["sample_size"], 0)
                self.assertIsInstance(config.get("latents"), dict)
                self.assertTrue(config["latents"])
                self.assertIsInstance(config.get("paths"), list)
                self.assertTrue(config["paths"])
                self.assertTrue(
                    all(indicators for indicators in config["latents"].values()),
                    "each latent should have at least one indicator",
                )

    def test_unknown_model_returns_none(self):
        self.assertIsNone(get_model_config("not-a-model"))

    def test_returned_configs_are_isolated_from_catalog_state(self):
        config = get_model_config("utaut")
        config_copy = copy.deepcopy(config)

        config["latents"].clear()

        self.assertEqual(get_model_config("utaut"), config_copy)


if __name__ == "__main__":
    unittest.main()
