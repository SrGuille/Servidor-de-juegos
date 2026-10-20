import json
import os
import unittest
from unittest.mock import patch

import django
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "servidor_juegos.settings")
django.setup()

from servidor import consumers
from servidor_juegos.asgi import application


class TestFlareCurseRoomConsumer(unittest.TestCase):
    async def _connect(self, path):
        communicator = WebsocketCommunicator(application, path)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        return communicator

    async def _receive_json(self, communicator, timeout=1.0):
        raw = await communicator.receive_from(timeout=timeout)
        return json.loads(raw)

    async def _connect_players(self, names):
        communicators = {}
        for name in names:
            communicator = await self._connect(f"/ws/flare_curse_room/?name={name}")
            snapshot = await self._receive_json(communicator)
            self.assertEqual("GameSnapshot", snapshot["type"])
            self.assertEqual(name, snapshot["you"]["name"])
            communicators[name] = communicator
        return communicators

    async def _disconnect_all(self, communicators):
        for communicator in communicators.values():
            await communicator.disconnect()

    def test_connect_returns_error_when_game_is_not_ready(self):
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=False):
            async_to_sync(self._test_connect_returns_error_when_game_is_not_ready)()

    async def _test_connect_returns_error_when_game_is_not_ready(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            payload = await self._receive_json(communicator)
            self.assertEqual("Error", payload["type"])
            self.assertIn("Flare Curse no esta listo", payload["message"])
        finally:
            await communicator.disconnect()

    def test_connect_with_player_sends_initial_snapshot(self):
        snapshot = {
            "type": "GameSnapshot",
            "you": {"name": "Ana"},
        }
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player", return_value=snapshot
        ) as snapshot_mock:
            async_to_sync(self._test_connect_with_player_sends_initial_snapshot)(snapshot)
            snapshot_mock.assert_called_once_with("Ana")

    async def _test_connect_with_player_sends_initial_snapshot(self, snapshot):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            payload = await self._receive_json(communicator)
            self.assertEqual(snapshot, payload)
        finally:
            await communicator.disconnect()

    def test_connect_snapshot_exception_returns_internal_error(self):
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine,
            "get_snapshot_for_player",
            side_effect=RuntimeError("snapshot failed"),
        ), self.assertLogs("servidor.consumers", level="ERROR") as logs:
            async_to_sync(self._test_connect_snapshot_exception_returns_internal_error)()

        self.assertTrue(any("snapshot failed player=Ana" in msg for msg in logs.output))

    async def _test_connect_snapshot_exception_returns_internal_error(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            payload = await self._receive_json(communicator)
            self.assertEqual("Error", payload["type"])
            self.assertEqual("Error interno de Flare Curse.", payload["message"])
        finally:
            await communicator.disconnect()

    def test_connect_without_player_does_not_send_snapshot(self):
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player"
        ) as snapshot_mock:
            async_to_sync(self._test_connect_without_player_does_not_send_snapshot)()
            snapshot_mock.assert_not_called()

    async def _test_connect_without_player_does_not_send_snapshot(self):
        communicator = await self._connect("/ws/flare_curse_room/")
        try:
            self.assertTrue(await communicator.receive_nothing(timeout=0.1))
        finally:
            await communicator.disconnect()

    def test_invalid_json_returns_error(self):
        snapshot = {"type": "GameSnapshot"}
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player", return_value=snapshot
        ):
            async_to_sync(self._test_invalid_json_returns_error)()

    async def _test_invalid_json_returns_error(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(communicator)  # Initial snapshot.
            await communicator.send_to(text_data="{invalid")
            payload = await self._receive_json(communicator)
            self.assertEqual("Error", payload["type"])
            self.assertEqual("Mensaje JSON invalido.", payload["message"])
        finally:
            await communicator.disconnect()

    def test_missing_action_returns_error(self):
        snapshot = {"type": "GameSnapshot"}
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player", return_value=snapshot
        ):
            async_to_sync(self._test_missing_action_returns_error)()

    async def _test_missing_action_returns_error(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(communicator)  # Initial snapshot.
            await communicator.send_to(text_data=json.dumps({"foo": "bar"}))
            payload = await self._receive_json(communicator)
            self.assertEqual("Error", payload["type"])
            self.assertEqual("Accion no indicada.", payload["message"])
        finally:
            await communicator.disconnect()

    def test_get_jugadores_requires_player_name(self):
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player"
        ) as snapshot_mock:
            async_to_sync(self._test_get_jugadores_requires_player_name)()
            snapshot_mock.assert_not_called()

    async def _test_get_jugadores_requires_player_name(self):
        communicator = await self._connect("/ws/flare_curse_room/")
        try:
            await communicator.send_to(text_data=json.dumps({"action": "GetJugadores"}))
            payload = await self._receive_json(communicator)
            self.assertEqual("Error", payload["type"])
            self.assertEqual("Este socket necesita un nombre de jugador.", payload["message"])
        finally:
            await communicator.disconnect()

    def test_mutating_action_requires_player_name_and_skips_engine_call(self):
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player"
        ) as snapshot_mock, patch.object(consumers.flare_curse_engine, "claim_flare") as claim_mock:
            async_to_sync(self._test_mutating_action_requires_player_name_and_skips_engine_call)()
            snapshot_mock.assert_not_called()
            claim_mock.assert_not_called()

    async def _test_mutating_action_requires_player_name_and_skips_engine_call(self):
        communicator = await self._connect("/ws/flare_curse_room/")
        try:
            await communicator.send_to(text_data=json.dumps({"action": "PedirDestello", "color": "red"}))
            payload = await self._receive_json(communicator)
            self.assertEqual("Error", payload["type"])
            self.assertEqual("Este socket necesita un nombre de jugador.", payload["message"])
        finally:
            await communicator.disconnect()

    def test_pedir_destello_returns_result_and_snapshot(self):
        snapshots = [
            {"type": "GameSnapshot", "step": "initial"},
            {"type": "GameSnapshot", "step": "after_claim"},
        ]
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player", side_effect=snapshots
        ) as snapshot_mock, patch.object(consumers.flare_curse_engine, "claim_flare", return_value=True) as claim_mock:
            async_to_sync(self._test_pedir_destello_returns_result_and_snapshot)()
            claim_mock.assert_called_once_with("Ana", "red")
            self.assertEqual(2, snapshot_mock.call_count)

    async def _test_pedir_destello_returns_result_and_snapshot(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(communicator)  # Initial snapshot.
            await communicator.send_to(text_data=json.dumps({"action": "PedirDestello", "color": "red"}))
            result_payload = await self._receive_json(communicator)
            snapshot_payload = await self._receive_json(communicator)

            self.assertEqual("PedirDestelloResult", result_payload["type"])
            self.assertTrue(result_payload["accepted"])
            self.assertEqual("red", result_payload["color"])
            self.assertEqual("GameSnapshot", snapshot_payload["type"])
            self.assertEqual("after_claim", snapshot_payload["step"])
        finally:
            await communicator.disconnect()

    def test_pedir_destello_engine_exception_returns_internal_error(self):
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine,
            "get_snapshot_for_player",
            return_value={"type": "GameSnapshot"},
        ), patch.object(
            consumers.flare_curse_engine,
            "claim_flare",
            side_effect=RuntimeError("claim failed"),
        ), self.assertLogs("servidor.consumers", level="ERROR") as logs:
            async_to_sync(self._test_pedir_destello_engine_exception_returns_internal_error)()

        self.assertTrue(any("PedirDestello failed player=Ana color=red" in msg for msg in logs.output))

    async def _test_pedir_destello_engine_exception_returns_internal_error(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(communicator)  # Initial snapshot.
            await communicator.send_to(text_data=json.dumps({"action": "PedirDestello", "color": "red"}))
            payload = await self._receive_json(communicator)
            self.assertEqual("Error", payload["type"])
            self.assertEqual("Error interno de Flare Curse.", payload["message"])
        finally:
            await communicator.disconnect()

    def test_lanzar_destello_fantasma_returns_result_and_snapshot(self):
        snapshots = [
            {"type": "GameSnapshot", "step": "initial"},
            {"type": "GameSnapshot", "step": "after_ghost"},
        ]
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player", side_effect=snapshots
        ), patch.object(consumers.flare_curse_engine, "launch_ghost_flare", return_value=(True, 3, 9.0)) as launch_mock:
            async_to_sync(self._test_lanzar_destello_fantasma_returns_result_and_snapshot)()
            launch_mock.assert_called_once_with("Ana")

    async def _test_lanzar_destello_fantasma_returns_result_and_snapshot(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(communicator)  # Initial snapshot.
            await communicator.send_to(text_data=json.dumps({"action": "LanzarDestelloFantasma"}))
            result_payload = await self._receive_json(communicator)
            snapshot_payload = await self._receive_json(communicator)

            self.assertEqual("LanzarDestelloFantasmaResult", result_payload["type"])
            self.assertTrue(result_payload["in_time"])
            self.assertEqual(3, result_payload["points"])
            self.assertEqual(9.0, result_payload["cooldown_seconds"])
            self.assertEqual("after_ghost", snapshot_payload["step"])
        finally:
            await communicator.disconnect()

    def test_maldecir_returns_result_and_snapshot(self):
        snapshots = [
            {"type": "GameSnapshot", "step": "initial"},
            {"type": "GameSnapshot", "step": "after_curse"},
        ]
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player", side_effect=snapshots
        ), patch.object(consumers.flare_curse_engine, "cast_curse", return_value=(True, False, "Ana")) as curse_mock:
            async_to_sync(self._test_maldecir_returns_result_and_snapshot)()
            curse_mock.assert_called_once_with("Ana", "Beto")

    async def _test_maldecir_returns_result_and_snapshot(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(communicator)  # Initial snapshot.
            await communicator.send_to(text_data=json.dumps({"action": "Maldecir", "target": "Beto"}))
            result_payload = await self._receive_json(communicator)
            snapshot_payload = await self._receive_json(communicator)

            self.assertEqual("MaldecirResult", result_payload["type"])
            self.assertTrue(result_payload["accepted"])
            self.assertFalse(result_payload["victim_is_enemy"])
            self.assertEqual("Ana", result_payload["cursed_player"])
            self.assertEqual("after_curse", snapshot_payload["step"])
        finally:
            await communicator.disconnect()

    def test_group_event_is_forwarded_to_client(self):
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine, "get_snapshot_for_player", return_value={"type": "GameSnapshot"}
        ):
            async_to_sync(self._test_group_event_is_forwarded_to_client)()

    async def _test_group_event_is_forwarded_to_client(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(communicator)  # Initial snapshot.

            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                consumers.ROOM_GROUP_NAME,
                {
                    "type": "flare_curse_event",
                    "payload": {"type": "PingConsumer", "value": 7},
                },
            )

            payload = await self._receive_json(communicator)
            self.assertEqual({"type": "PingConsumer", "value": 7}, payload)
        finally:
            await communicator.disconnect()

    def test_multiclient_room_broadcast_reaches_all_players(self):
        def snapshot_for(player_name):
            return {"type": "GameSnapshot", "you": {"name": player_name}}

        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine,
            "get_snapshot_for_player",
            side_effect=snapshot_for,
        ):
            async_to_sync(self._test_multiclient_room_broadcast_reaches_all_players)()

    async def _test_multiclient_room_broadcast_reaches_all_players(self):
        communicators = await self._connect_players(["Ana", "Beto", "Caro"])
        try:
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                consumers.ROOM_GROUP_NAME,
                {
                    "type": "flare_curse_event",
                    "payload": {"type": "SmokeBroadcast", "tick": 1},
                },
            )

            for communicator in communicators.values():
                payload = await self._receive_json(communicator)
                self.assertEqual({"type": "SmokeBroadcast", "tick": 1}, payload)
        finally:
            await self._disconnect_all(communicators)

    def test_multiclient_private_event_reaches_only_target_player(self):
        def snapshot_for(player_name):
            return {"type": "GameSnapshot", "you": {"name": player_name}}

        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine,
            "get_snapshot_for_player",
            side_effect=snapshot_for,
        ):
            async_to_sync(self._test_multiclient_private_event_reaches_only_target_player)()

    async def _test_multiclient_private_event_reaches_only_target_player(self):
        communicators = await self._connect_players(["Ana", "Beto", "Caro"])
        try:
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                consumers.get_player_group_name("Beto"),
                {
                    "type": "flare_curse_event",
                    "payload": {"type": "PrivatePing", "to": "Beto"},
                },
            )

            beto_payload = await self._receive_json(communicators["Beto"])
            self.assertEqual({"type": "PrivatePing", "to": "Beto"}, beto_payload)
            self.assertTrue(await communicators["Ana"].receive_nothing(timeout=0.1))
            self.assertTrue(await communicators["Caro"].receive_nothing(timeout=0.1))
        finally:
            await self._disconnect_all(communicators)

    def test_private_event_reaches_all_connections_with_same_player_name(self):
        def snapshot_for(player_name):
            return {"type": "GameSnapshot", "you": {"name": player_name}}

        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine,
            "get_snapshot_for_player",
            side_effect=snapshot_for,
        ):
            async_to_sync(self._test_private_event_reaches_all_connections_with_same_player_name)()

    async def _test_private_event_reaches_all_connections_with_same_player_name(self):
        comm_one = await self._connect("/ws/flare_curse_room/?name=Ana")
        comm_two = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(comm_one)
            await self._receive_json(comm_two)

            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                consumers.get_player_group_name("Ana"),
                {
                    "type": "flare_curse_event",
                    "payload": {"type": "PrivateTwin", "to": "Ana"},
                },
            )

            payload_one = await self._receive_json(comm_one)
            payload_two = await self._receive_json(comm_two)
            self.assertEqual({"type": "PrivateTwin", "to": "Ana"}, payload_one)
            self.assertEqual({"type": "PrivateTwin", "to": "Ana"}, payload_two)
        finally:
            await comm_one.disconnect()
            await comm_two.disconnect()

    def test_action_result_then_internal_error_when_snapshot_fails(self):
        snapshots = [
            {"type": "GameSnapshot", "step": "initial"},
            RuntimeError("snapshot failed after action"),
        ]
        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine,
            "get_snapshot_for_player",
            side_effect=snapshots,
        ), patch.object(consumers.flare_curse_engine, "claim_flare", return_value=True), self.assertLogs(
            "servidor.consumers", level="ERROR"
        ) as logs:
            async_to_sync(self._test_action_result_then_internal_error_when_snapshot_fails)()

        self.assertTrue(any("snapshot failed player=Ana" in msg for msg in logs.output))

    async def _test_action_result_then_internal_error_when_snapshot_fails(self):
        communicator = await self._connect("/ws/flare_curse_room/?name=Ana")
        try:
            await self._receive_json(communicator)  # Initial snapshot.
            await communicator.send_to(text_data=json.dumps({"action": "PedirDestello", "color": "red"}))

            result_payload = await self._receive_json(communicator)
            error_payload = await self._receive_json(communicator)

            self.assertEqual("PedirDestelloResult", result_payload["type"])
            self.assertTrue(result_payload["accepted"])
            self.assertEqual("Error", error_payload["type"])
            self.assertEqual("Error interno de Flare Curse.", error_payload["message"])
        finally:
            await communicator.disconnect()

    def test_multiclient_action_result_is_sent_only_to_sender(self):
        def snapshot_for(player_name):
            return {"type": "GameSnapshot", "you": {"name": player_name}}

        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine,
            "get_snapshot_for_player",
            side_effect=snapshot_for,
        ), patch.object(consumers.flare_curse_engine, "claim_flare", return_value=False):
            async_to_sync(self._test_multiclient_action_result_is_sent_only_to_sender)()

    async def _test_multiclient_action_result_is_sent_only_to_sender(self):
        communicators = await self._connect_players(["Ana", "Beto"])
        try:
            await communicators["Ana"].send_to(text_data=json.dumps({"action": "PedirDestello", "color": "red"}))

            ana_result = await self._receive_json(communicators["Ana"])
            ana_snapshot = await self._receive_json(communicators["Ana"])
            self.assertEqual("PedirDestelloResult", ana_result["type"])
            self.assertFalse(ana_result["accepted"])
            self.assertEqual("GameSnapshot", ana_snapshot["type"])
            self.assertEqual("Ana", ana_snapshot["you"]["name"])

            self.assertTrue(await communicators["Beto"].receive_nothing(timeout=0.1))
        finally:
            await self._disconnect_all(communicators)

    def test_multiclient_maldecir_same_target_second_is_rejected(self):
        def snapshot_for(player_name):
            return {"type": "GameSnapshot", "you": {"name": player_name}}

        with patch.object(consumers.flare_curse_engine, "ensure_started", return_value=True), patch.object(
            consumers.flare_curse_engine,
            "get_snapshot_for_player",
            side_effect=snapshot_for,
        ), patch.object(
            consumers.flare_curse_engine,
            "cast_curse",
            side_effect=[(True, True, "Beto"), (False, False, None)],
        ) as curse_mock:
            async_to_sync(self._test_multiclient_maldecir_same_target_second_is_rejected)()
            self.assertEqual(2, curse_mock.call_count)
            self.assertEqual(("Ana", "Beto"), curse_mock.call_args_list[0][0])
            self.assertEqual(("Caro", "Beto"), curse_mock.call_args_list[1][0])

    async def _test_multiclient_maldecir_same_target_second_is_rejected(self):
        communicators = await self._connect_players(["Ana", "Caro"])
        try:
            await communicators["Ana"].send_to(text_data=json.dumps({"action": "Maldecir", "target": "Beto"}))
            ana_result = await self._receive_json(communicators["Ana"])
            ana_snapshot = await self._receive_json(communicators["Ana"])

            self.assertEqual("MaldecirResult", ana_result["type"])
            self.assertTrue(ana_result["accepted"])
            self.assertTrue(ana_result["victim_is_enemy"])
            self.assertEqual("Beto", ana_result["cursed_player"])
            self.assertEqual("GameSnapshot", ana_snapshot["type"])

            await communicators["Caro"].send_to(text_data=json.dumps({"action": "Maldecir", "target": "Beto"}))
            caro_result = await self._receive_json(communicators["Caro"])
            caro_snapshot = await self._receive_json(communicators["Caro"])

            self.assertEqual("MaldecirResult", caro_result["type"])
            self.assertFalse(caro_result["accepted"])
            self.assertFalse(caro_result["victim_is_enemy"])
            self.assertIsNone(caro_result["cursed_player"])
            self.assertEqual("GameSnapshot", caro_snapshot["type"])
        finally:
            await self._disconnect_all(communicators)


if __name__ == "__main__":
    unittest.main()