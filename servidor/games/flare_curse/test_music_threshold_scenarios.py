import os
import tempfile
import unittest

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "servidor_juegos.settings")
django.setup()

from servidor.games.flare_curse import music_threshold_scenarios as scenarios


class TestFlareCurseMatchSimulation(unittest.TestCase):
    def _build_match_args(self, extra_args=None):
        parser = scenarios.build_parser()
        args_list = [
            "--model",
            "match",
            "--players",
            "9",
            "--seed",
            "13579",
            "--dt-seconds",
            "0.25",
            "--max-sim-seconds",
            "90",
            "--max-attempts",
            "3",
            "--output-dir",
            tempfile.gettempdir(),
        ]
        if extra_args:
            args_list.extend(extra_args)
        return parser.parse_args(args_list)

    def test_simulation_is_deterministic_for_same_seed(self):
        args = self._build_match_args(["--max-attempts", "1", "--require-single-survivor"])

        result_a = scenarios._simulate_single_match(args, seed=args.seed, attempt=1)
        result_b = scenarios._simulate_single_match(args, seed=args.seed, attempt=1)

        self.assertEqual(result_a.ended, result_b.ended)
        self.assertEqual(result_a.end_reason, result_b.end_reason)
        self.assertEqual(result_a.duration_seconds, result_b.duration_seconds)
        self.assertEqual(result_a.winner_team, result_b.winner_team)
        self.assertEqual(result_a.winner_alive_count, result_b.winner_alive_count)
        self.assertEqual(result_a.event_counts, result_b.event_counts)
        self.assertEqual(result_a.timeline_rows, result_b.timeline_rows)

    def test_retry_wrapper_stops_early_when_single_survivor_not_required(self):
        args = self._build_match_args(["--no-require-single-survivor", "--max-attempts", "5"])

        result, summaries, requirement_met = scenarios._simulate_match_with_retries(args)

        self.assertTrue(requirement_met)
        self.assertEqual(1, len(summaries))
        self.assertEqual(1, result.attempt)
        self.assertGreater(len(result.timeline_rows), 0)

    def test_csv_and_plot_outputs_are_generated(self):
        args = self._build_match_args(["--max-attempts", "1", "--max-sim-seconds", "45"])
        result = scenarios._simulate_single_match(args, seed=args.seed, attempt=1)

        self.assertGreater(len(result.timeline_rows), 0)

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = os.path.join(temp_dir, "timeline.csv")
            png_path = os.path.join(temp_dir, "timeline.png")
            context_txt_path = os.path.join(temp_dir, "timeline_context.txt")

            scenarios._write_match_csv(result.timeline_rows, csv_path)
            scenarios._write_match_events_context_output(result.timeline_rows, context_txt_path)
            scenarios._plot_match_intensity(
                rows=result.timeline_rows,
                output_png_path=png_path,
                high_threshold=args.high_threshold,
                low_threshold=args.low_threshold,
            )

            self.assertTrue(os.path.exists(csv_path))
            self.assertTrue(os.path.exists(png_path))
            self.assertTrue(os.path.exists(context_txt_path))
            self.assertGreater(os.path.getsize(csv_path), 0)
            self.assertGreater(os.path.getsize(png_path), 0)
            self.assertGreater(os.path.getsize(context_txt_path), 0)

            with open(csv_path, "r", encoding="utf-8") as csv_file:
                header = csv_file.readline().strip()

            self.assertIn("intensity_score", header)
            self.assertIn("dominant_event", header)
            self.assertIn("colors_in_hand_norm", header)
            self.assertIn("recent_flares_norm", header)
            self.assertIn("recent_curses_norm", header)
            self.assertIn("launch_flare_colors", header)

            with open(context_txt_path, "r", encoding="utf-8") as context_file:
                context_text = context_file.read()

            self.assertIn("### Output (stdout and stderr interleaved):", context_text)
            self.assertIn("```", context_text)
            self.assertIn("time | alive | limit | offered | launch_flare_colors | mode | score | events", context_text)


if __name__ == "__main__":
    unittest.main()
