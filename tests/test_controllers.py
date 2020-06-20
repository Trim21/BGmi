import unittest

from bgmi.lib.constants import BANGUMI_UPDATE_TIME
from bgmi.lib.controllers import (
    Bangumi,
    add,
    cal,
    delete,
    filter_,
    mark,
    recreate_source_relatively_table,
    search,
)
from bgmi.lib.models import Filter, Subtitle
from bgmi.main import setup

bangumi_name_1 = "名侦探柯南"
bangumi_name_2 = "海贼王"

subtitle_1 = [
    "5492bc5bcce0187a129979d7",
    "5492ecbc2a934ba5288acb20",
    "567bda4eafc701435d468b61",
    "581be821ee98e9ca20730eae",
    "59af67e5d04829c1623b0e51",
]

# def test_a_cal():
#     r = cal()
#     assert isinstance(r, dict)
#     for day in r.keys():
#         assert day.lower() in [x.lower() for x in BANGUMI_UPDATE_TIME]
#         assert isinstance(r[day], list)
#         for bangumi in r[day]:
#             assert "status" in bangumi
#             assert "subtitle_group" in bangumi
#             assert "name" in bangumi
#             assert "update_time" in bangumi
#             assert "cover" in bangumi


class ControllersTest(unittest.TestCase):
    def setUp(self):
        self.bangumi_name_1 = "名侦探柯南"
        self.bangumi_name_2 = "海贼王"

    def test_a_cal(self):
        r = cal()
        self.assertIsInstance(r, dict)
        for day in r.keys():
            self.assertIn(day.lower(), [x.lower() for x in BANGUMI_UPDATE_TIME])
            self.assertIsInstance(r[day], list)
            for bangumi in r[day]:
                self.assertIn("status", bangumi)
                self.assertIn("subtitle_group", bangumi)
                self.assertIn("name", bangumi)
                self.assertIn("update_time", bangumi)
                self.assertIn("cover", bangumi)

    def test_b_add(self):
        r = add(self.bangumi_name_1, 0)
        assert r.status == "success", r["message"]
        r = add(self.bangumi_name_1, 0)
        assert r.status == "warning", r["message"]
        r = delete(self.bangumi_name_1)
        assert r.status == "warning", r.message

    def test_c_mark(self):
        add(self.bangumi_name_1, 0)

        r = mark(self.bangumi_name_1, 1)
        self.assertEqual(r["status"], "success", r["message"])
        r = mark(self.bangumi_name_1, None)
        self.assertEqual(r["status"], "info", r["message"])
        r = mark(self.bangumi_name_2, 0)
        self.assertEqual(r["status"], "error", r["message"])

    def test_d_delete(self):
        r = delete()
        self.assertEqual(r.status, "warning", r.message)
        r = delete(self.bangumi_name_1)
        self.assertEqual(r.status, "warning", r.message)
        r = delete(self.bangumi_name_1)
        self.assertEqual(r.status, "warning", r.message)
        r = delete(self.bangumi_name_2)
        self.assertEqual(r.status, "error", r.message)
        r = delete(clear_all=True, batch=True)
        self.assertEqual(r.status, "warning", r.message)

    def test_e_search(self):
        r = search(self.bangumi_name_1, dupe=False)

    @staticmethod
    def setUpClass():
        setup()
        recreate_source_relatively_table()


def test_filter_include(clean_bgmi):
    Filter.delete().where(Filter.bangumi_name == bangumi_name_1).execute()
    add(bangumi_name_1, 0)
    filter_(bangumi_name_1, include="a,b,c")
    assert (
        Filter.get(bangumi_name=bangumi_name_1).include == "a,b,c"
    ), "include should same with db"


def test_filter_exclude(clean_bgmi):
    Filter.delete().where(Filter.bangumi_name == bangumi_name_1).execute()
    add(bangumi_name_1, 0)
    filter_(bangumi_name_1, exclude="a,b,c")
    assert (
        Filter.get(bangumi_name=bangumi_name_1).exclude == "a,b,c"
    ), "exclude should same with db"


def test_filter_regex(clean_bgmi):
    Filter.delete().where(Filter.bangumi_name == bangumi_name_1).execute()
    add(bangumi_name_1, 0)
    filter_(bangumi_name_1, regex=".*720.*")
    assert (
        Filter.get(bangumi_name=bangumi_name_1).regex == ".*720.*"
    ), "regex should same with db"


def test_filter_subtitle(clean_bgmi):
    Filter.delete().where(Filter.bangumi_name == bangumi_name_1).execute()
    add(bangumi_name_1, 0)
    assert list(Bangumi.select().where(Bangumi.name == bangumi_name_1))
    subtitle_list = Subtitle.get_subtitle_by_id(subtitle_1[:2])

    filter_(bangumi_name_1, subtitle=",".join([x["name"] for x in subtitle_list]))
    f = Filter.get(bangumi_name=bangumi_name_1)
    assert {x.strip() for x in f.subtitle.split(",")} == {
        x["id"] for x in subtitle_list
    }, "subtitle should same with db"
