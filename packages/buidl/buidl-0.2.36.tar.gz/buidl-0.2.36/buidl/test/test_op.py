from io import BytesIO

from buidl.op import (
    decode_num,
    encode_num,
    op_checklocktimeverify,
    op_checkmultisig,
    op_checksequenceverify,
    op_checksig,
    op_hash160,
)
from buidl.script import Script
from buidl.timelock import Locktime, Sequence
from buidl.tx import Tx, TxIn, TxOut

from buidl.test import OfflineTestCase


class OpTest(OfflineTestCase):
    def test_op_hash160(self):
        stack = [b"hello world"]
        self.assertTrue(op_hash160(stack))
        self.assertEqual(stack[0].hex(), "d7d5ee7824ff93f94c3055af9382c86c68b5ca92")

    def test_op_checksig(self):
        tests = (
            (
                "010000000148dcc16482f5c835828020498ec1c35f48a578585721b5a77445a4ce93334d18000000006a4730440220636b9f822ea2f85e6375ecd066a49cc74c20ec4f7cf0485bebe6cc68da92d8ce022068ae17620b12d99353287d6224740b585ff89024370a3212b583fb454dce7c160121021f955d36390a38361530fb3724a835f4f504049492224a028fb0ab8c063511a7ffffffff0220960705000000001976a914d23541bd04c58a1265e78be912e63b2557fb439088aca0860100000000001976a91456d95dc3f2414a210efb7188d287bff487df96c688ac00000000",
                "30440220636b9f822ea2f85e6375ecd066a49cc74c20ec4f7cf0485bebe6cc68da92d8ce022068ae17620b12d99353287d6224740b585ff89024370a3212b583fb454dce7c1601",
                "021f955d36390a38361530fb3724a835f4f504049492224a028fb0ab8c063511a7",
                "testnet",
            ),
            (
                "01000000000101e92e1c1d29218348f8ec9463a9fc94670f675a7f82ae100f3e8a5cbd63b4192e0100000017160014d52ad7ca9b3d096a38e752c2018e6fbc40cdf26fffffffff014c400f00000000001976a9146e13971913b9aa89659a9f53d327baa8826f2d7588ac0247304402205e3ae5ac9a0e0a16ae04b0678c5732973ce31051ba9f42193e69843e600d84f2022060a91cbd48899b1bf5d1ffb7532f69ab74bc1701a253a415196b38feb599163b012103935581e52c354cd2f484fe8ed83af7a3097005b2f9c60bff71d35bd795f54b6700000000",
                "304402205e3ae5ac9a0e0a16ae04b0678c5732973ce31051ba9f42193e69843e600d84f2022060a91cbd48899b1bf5d1ffb7532f69ab74bc1701a253a415196b38feb599163b01",
                "03935581e52c354cd2f484fe8ed83af7a3097005b2f9c60bff71d35bd795f54b67",
                "testnet",
            ),
            (
                "0200000000010140d43a99926d43eb0e619bf0b3d83b4a31f60c176beecfb9d35bf45e54d0f7420100000017160014a4b4ca48de0b3fffc15404a1acdc8dbaae226955ffffffff0100e1f5050000000017a9144a1154d50b03292b3024370901711946cb7cccc387024830450221008604ef8f6d8afa892dee0f31259b6ce02dd70c545cfcfed8148179971876c54a022076d771d6e91bed212783c9b06e0de600fab2d518fad6f15a2b191d7fbd262a3e0121039d25ab79f41f75ceaf882411fd41fa670a4c672c23ffaf0e361a969cde0692e800000000",
                "30450221008604ef8f6d8afa892dee0f31259b6ce02dd70c545cfcfed8148179971876c54a022076d771d6e91bed212783c9b06e0de600fab2d518fad6f15a2b191d7fbd262a3e01",
                "039d25ab79f41f75ceaf882411fd41fa670a4c672c23ffaf0e361a969cde0692e8",
                "mainnet",
            ),
        )
        for raw_tx, sig_hex, sec_hex, network in tests:
            tx_obj = Tx.parse(BytesIO(bytes.fromhex(raw_tx)), network=network)
            sec = bytes.fromhex(sec_hex)
            sig = bytes.fromhex(sig_hex)
            stack = [sig, sec]
            self.assertTrue(op_checksig(stack, tx_obj, 0))
            self.assertEqual(decode_num(stack[0]), 1)

    def test_op_checkmultisig(self):
        raw_tx = "0100000001868278ed6ddfb6c1ed3ad5f8181eb0c7a385aa0836f01d5e4789e6bd304d87221a000000db00483045022100dc92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a8993701483045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e75402201475221022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb702103b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb7152aeffffffff04d3b11400000000001976a914904a49878c0adfc3aa05de7afad2cc15f483a56a88ac7f400900000000001976a914418327e3f3dda4cf5b9089325a4b95abdfa0334088ac722c0c00000000001976a914ba35042cfe9fc66fd35ac2224eebdafd1028ad2788acdc4ace020000000017a91474d691da1574e6b3c192ecfb52cc8984ee7b6c568700000000"
        tx_obj = Tx.parse(BytesIO(bytes.fromhex(raw_tx)))
        sig1 = bytes.fromhex(
            "3045022100dc92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a8993701"
        )
        sig2 = bytes.fromhex(
            "3045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e75402201"
        )
        sec1 = bytes.fromhex(
            "022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb70"
        )
        sec2 = bytes.fromhex(
            "03b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb71"
        )
        stack = [b"", sig1, sig2, b"\x02", sec1, sec2, b"\x02"]
        self.assertTrue(op_checkmultisig(stack, tx_obj, 0))
        self.assertEqual(decode_num(stack[0]), 1)

    def test_op_cltv(self):
        locktime_0 = Locktime(1234)
        locktime_1 = Locktime(2345)
        sequence = Sequence()
        tx_in = TxIn(b"\x00" * 32, 0, sequence=sequence)
        tx_out = TxOut(1, Script())
        tx_obj = Tx(1, [tx_in], [tx_out], locktime_1)
        stack = []
        self.assertFalse(op_checklocktimeverify(stack, tx_obj, 0))
        tx_in.sequence = Sequence(0xFFFFFFFE)
        self.assertFalse(op_checklocktimeverify(stack, tx_obj, 0))
        stack = [encode_num(-5)]
        self.assertFalse(op_checklocktimeverify(stack, tx_obj, 0))
        stack = [encode_num(locktime_0)]
        self.assertTrue(op_checklocktimeverify(stack, tx_obj, 0))
        tx_obj.locktime = Locktime(1582820194)
        self.assertFalse(op_checklocktimeverify(stack, tx_obj, 0))
        tx_obj.locktime = Locktime(500)
        self.assertFalse(op_checklocktimeverify(stack, tx_obj, 0))

    def test_op_csv(self):
        sequence_0 = Sequence()
        sequence_1 = Sequence(2345)
        tx_in = TxIn(b"\x00" * 32, 0, sequence=sequence_0)
        tx_out = TxOut(1, Script())
        tx_obj = Tx(1, [tx_in], [tx_out])
        stack = []
        self.assertFalse(op_checksequenceverify(stack, tx_obj, 0))
        tx_in.sequence = sequence_1
        self.assertFalse(op_checksequenceverify(stack, tx_obj, 0))
        stack = [encode_num(-5)]
        self.assertFalse(op_checksequenceverify(stack, tx_obj, 0))
        tx_obj.version = 2
        self.assertFalse(op_checksequenceverify(stack, tx_obj, 0))
        stack = [encode_num(1234 | (1 << 22))]
        self.assertFalse(op_checksequenceverify(stack, tx_obj, 0))
        stack = [encode_num(9999)]
        self.assertFalse(op_checksequenceverify(stack, tx_obj, 0))
        stack = [encode_num(1234)]
        self.assertTrue(op_checksequenceverify(stack, tx_obj, 0))
