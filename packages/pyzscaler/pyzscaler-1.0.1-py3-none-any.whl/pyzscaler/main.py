import json

from pyzscaler import ZPA, ZIA
from pprint import pprint

zpa = ZPA()

for idp in zpa.idp.list_idps():
    pprint(f"ID: {idp.id} || Name: {idp.name}")

pprint(zpa.scim_groups.get_group("456447", all_entries=True))

for group in zpa.scim_groups.list_groups("216196382959075592"):
    pprint(group)
# for item in zpa.lss.list_client_types():
#     pprint(item)
#
# for item in zpa.lss.list_log_formats():
#     pprint(item)

# for item in zpa.lss.list_configs():
#     pprint(item)

#info_sesh_codes = zpa.lss.list_session_status_codes()['error']
# pprint(zpa.lss.add_lss_config(
#     name="apitest12",
#     app_connector_group_ids=["216196382959075361"],
#     lss_host="1.1.1.1",
#     lss_port="80",
#     audit_message="blank",
#     log_stream_content="",
#     filter_status_codes=info_sesh_codes,
#     policy_rules=[("idp", ["216196382959075341"]),
#                   ("client_type", ["zpn_client_type_exporter"]),
#                   ("app", ["216196382959075617"]),
#                   ("app_group", ["216196382959075614"]),
#                   ("saml", [("216196382959075548", "test3"),
#                             ("216196382959075548", "test4")])],
#     policy_name="my_policy"
# ))

# print(zpa.lss.update_lss_config("216196382959075618",
#                                 filter_status_codes=info_sesh_codes,
#                                 policy_rules=[("idp", ["216196382959075341"]),
#                                               ("app", ["216196382959075617"]),
#                                               ("app_group", ["216196382959075614"]),
#                                               ("saml", [("216196382959075548", "test3")
#                                                         ])]))

# with ZIA() as zia:
#     pprint(zia.dlp.get_engine('64'))
