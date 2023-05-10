import asyncio
import json
import os
import shelve
import sys
import traceback
from datetime import datetime

import flet as ft
from flet.security import encrypt, decrypt
from flet_core import TextThemeStyle, CrossAxisAlignment, ThemeMode, Margin, MainAxisAlignment, Alignment, Page, \
    ButtonStyle, ScrollMode

import flagship.hits
from flagship import Flagship, Visitor
from flagship.cache_manager import SqliteCacheManager
from flagship.config import DecisionApi, Bucketing
from flagship.flag import Flag
from flagship.hits import Screen, Event, EventCategory, Transaction, Item
from flagship.log_manager import LogManager, LogLevel
from flagship.tracking_manager import TrackingManagerConfig, CacheStrategy
from flagship.utils import pretty_dict


class SideBar(ft.UserControl):
    def __init__(self, page: Page, on_page_changed):
        super().__init__()
        self.page = page
        self.on_page_changed = on_page_changed

    def build(self):
        rail = ft.NavigationRail(
            selected_index=0,
            expand=True,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            group_alignment=-0.8,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="Configuration",
                    padding=ft.Padding(0, 10, 0, 10)

                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.ACCOUNT_CIRCLE_OUTLINED),
                    selected_icon_content=ft.Icon(ft.icons.ACCOUNT_CIRCLE),
                    label="Visitor",
                    padding=ft.Padding(0, 10, 0, 10)
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FLAG_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.FLAG),
                    label_content=ft.Text("Flags"),
                    padding=ft.Padding(0, 10, 0, 10)
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SEND_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.SEND),
                    label_content=ft.Text("Hits"),
                    padding=ft.Padding(0, 10, 0, 10)
                ),
            ],
            on_change=lambda e: self.on_page_changed(e.control.selected_index),
        )
        return rail


class ConfigurationView(ft.Container):

    def __init__(self, page: Page, log_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.log_manager = log_manager
        self.env_id_field = ft.TextField(border_color='#919993')
        self.api_key_field = ft.TextField(border_color='#919993', password=True, can_reveal_password=True)
        asyncio.run(asyncio.wait_for(self.decrypt_and_load_from_cache(True), timeout=1))
        self.mode_dropdown = ft.Dropdown(border_color='#919993', width=300,
                                         options=[ft.dropdown.Option("API"), ft.dropdown.Option("BUCKETING")])
        self.mode_dropdown.value = "API"
        self.polling_interval_field = ft.TextField(border_color='#919993', value="60000")
        self.timeout_field = ft.TextField(border_color='#919993', value="2000")
        self.tracking_manager_interval_field = ft.TextField(border_color='#919993', value="10000")
        self.tracking_manager_max_field = ft.TextField(border_color='#919993', value="20")
        self.tracking_manager_timeout_field = ft.TextField(border_color='#919993', value="200")
        self.tracking_manager_strategy_dropdown = ft.Dropdown(border_color='#919993', width=300,
                                                              options=[ft.dropdown.Option("CONTINUOUS"),
                                                                       ft.dropdown.Option("PERIODIC"),
                                                                       ft.dropdown.Option("NO BATCHING")],
                                                              value="CONTINUOUS")
        self.padding = ft.Padding(20, 0, 0, 0),
        self.content = ft.Column(
            spacing=20,
            controls=[
                ft.Container(
                    padding=ft.Padding(0, 0, 0, 20),
                    content=ft.Text("Configuration", style=TextThemeStyle.TITLE_LARGE, color='#FF8974')
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Env id: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993', width=300),
                        self.env_id_field
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Api key: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993', width=300),
                        self.api_key_field
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Mode: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993', width=300),
                        self.mode_dropdown
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Polling interval (in ms): ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993'
                                , width=300),
                        self.polling_interval_field
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Timeout (in ms): ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993'
                                , width=300),
                        self.timeout_field
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Tracking Manager - strategy: ", style=TextThemeStyle.TITLE_MEDIUM,
                                color='#919993',
                                width=300),
                        self.tracking_manager_strategy_dropdown
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Tracking Manager - intervals (in ms): ", style=TextThemeStyle.TITLE_MEDIUM,
                                color='#919993',
                                width=300),
                        self.tracking_manager_interval_field
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Tracking Manager - max pool size: ", style=TextThemeStyle.TITLE_MEDIUM,
                                color='#919993',
                                width=300),
                        self.tracking_manager_max_field
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Tracking Manager - timeout (in ms): ", style=TextThemeStyle.TITLE_MEDIUM,
                                color='#919993',
                                width=300),
                        self.tracking_manager_timeout_field
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            margin=Margin(0, 40, 0, 0),
                            content=ft.FilledButton(
                                text="Start",
                                style=ButtonStyle(
                                    overlay_color="#d13288"
                                ),
                                on_click=self.start_flagship,
                                width=300)
                        ),
                        ft.Container(
                            margin=Margin(0, 40, 0, 0),
                            content=ft.FilledButton(
                                text="Stop",
                                style=ButtonStyle(
                                    overlay_color="#d13288"
                                ),
                                on_click=self.stop_flagship,
                                width=300)
                        )
                    ]
                ),
            ]
        )

    def start_flagship(self, e):

        try:
            if self.tracking_manager_strategy_dropdown.value == "PERIODIC":
                strategy = CacheStrategy.PERIODIC_CACHING
            elif self.tracking_manager_strategy_dropdown.value == "NO BATCHING":
                strategy = CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING
            else:
                strategy = CacheStrategy.CONTINUOUS_CACHING
            tracking_config = TrackingManagerConfig(cache_strategy=strategy,
                                                    timeout=int(self.tracking_manager_timeout_field.value),
                                                    max_pool_size=int(self.tracking_manager_max_field.value),
                                                    time_interval=int(self.tracking_manager_interval_field.value))
            if self.mode_dropdown.value == "API":
                conf = DecisionApi(timeout=int(self.timeout_field.value), log_manager=self.log_manager,
                                   tracking_manager_config=tracking_config, cache_manager=SqliteCacheManager())
            elif self.mode_dropdown.value == "BUCKETING":
                conf = Bucketing(timeout=int(self.timeout_field.value),
                                 polling_interval=int(self.polling_interval_field.value), log_manager=self.log_manager,
                                 tracking_manager_config=tracking_config,
                                 cache_manager=SqliteCacheManager())
            else:
                conf = None
            if conf is not None:
                asyncio.run(self.encrypt_and_cache_conf())
                Flagship.start(self.env_id_field.value, self.api_key_field.value, conf)
        except Exception as e:
            print(traceback.format_exc())

    def stop_flagship(self, e):
        Flagship.stop()

    # def on_content_displayed(self, init=False):
    #     asyncio.run(self.decrypt_and_load_from_cache(init))

    async def decrypt_and_load_from_cache(self, init=False):
        try:

            secret_key = os.getenv("QA_APP_SECRET")
            # if self.page.client_storage.contains_key("envId") and self.page.client_storage.contains_key("apiKey"):
            env_id = self.page.client_storage.get("envId")
            api_key = self.page.client_storage.get("apiKey")
            if secret_key is not None:
                if env_id is not None:
                    self.env_id_field.value = decrypt(env_id, secret_key)
                    if not init:
                        self.env_id_field.update()
                if api_key is not None:
                    self.api_key_field.value = decrypt(api_key, secret_key)
                    if not init:
                        self.api_key_field.update()
            else:
                print("===== Set QA_APP_SECRET env variable to cache ids =====")
        except Exception as e:
            print("QA_APP : 'decrypt_and_load_from_cache' error.")
            # print(traceback.print_exc())

    async def encrypt_and_cache_conf(self):
        secret_key = os.getenv("QA_APP_SECRET")
        if secret_key is not None:
            self.page.client_storage.set("envId", encrypt(self.env_id_field.value, secret_key))
            self.page.client_storage.set("apiKey", encrypt(self.api_key_field.value, secret_key))


class VisitorView(ft.Container):

    def __init__(self, page: Page, visitor, on_visitor_synchronized, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.on_visitor_synchronized = on_visitor_synchronized
        self.visitor = visitor
        self.visitor_id_field = ft.TextField(border_color='#919993')
        self.anonymous_id_field = ft.TextField(border_color='#919993', read_only=True)
        self.authenticated_switch = ft.Switch(value=False)
        self.consent_switch = ft.Switch(value=True)
        self.context_field = ft.TextField(border_color='#919993', value="{\n\n\n\n\n\n\n\n\n}", width=300,
                                          multiline=True, min_lines=10, max_lines=10)
        self.update_context_field = ft.TextField(border_color='#919993', value="{\n\n\n\n\n\n\n\n\n}", width=600,
                                                 multiline=True, min_lines=10, max_lines=10)
        self.authenticate_field = ft.TextField(border_color='#919993')
        self.update_consent_switch = ft.Switch(value=True, on_change=self.on_consent_changed)
        self.load_visitor_from_cache()
        self.content = ft.Stack(
            controls=[
                ft.Column(
                    spacing=20,
                    scroll=ScrollMode.ALWAYS,
                    controls=[
                        ft.Container(
                            padding=ft.Padding(0, 0, 0, 20),
                            content=ft.Text("Visitor", style=TextThemeStyle.TITLE_LARGE, color='#FF8974')
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Visitor id: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993'
                                        , width=300),
                                self.visitor_id_field
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Anonymous id: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                        disabled=True
                                        , width=300),
                                self.anonymous_id_field
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Authenticated: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                        width=300),
                                ft.Container(
                                    width=300,
                                    alignment=Alignment(-1, 0),
                                    content=self.authenticated_switch,
                                )
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Has consented: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                        width=300),
                                ft.Container(
                                    width=300,
                                    alignment=Alignment(-1, 0),
                                    content=self.consent_switch,
                                )
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            vertical_alignment=CrossAxisAlignment.START,
                            controls=[
                                ft.Text("Context: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993', width=300),
                                self.context_field
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.FilledButton(text="Create visitor", style=ButtonStyle(overlay_color="#d13288"),
                                                on_click=self.on_visitor_created_click,
                                                width=600),
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            vertical_alignment=CrossAxisAlignment.START,
                            controls=[
                                ft.Text("Update context: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                        width=600),
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            vertical_alignment=CrossAxisAlignment.START,
                            controls=[
                                self.update_context_field,
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.FilledButton(text="Update context", style=ButtonStyle(overlay_color="#d13288"),
                                                on_click=self.on_update_context_click,
                                                width=600),
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Authenticate: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                        disabled=True
                                        , width=300),
                                self.authenticate_field
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.FilledButton(text="Authenticate", style=ButtonStyle(overlay_color="#d13288"),
                                                on_click=self.on_authenticate_click,
                                                width=600),
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.FilledButton(text="UnAuthenticate", style=ButtonStyle(overlay_color="#d13288"),
                                                on_click=self.on_unauthenticate_click,
                                                width=600),
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Has consented: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                        width=300),
                                ft.Container(
                                    width=300,
                                    alignment=Alignment(-1, 0),
                                    content=self.update_consent_switch,
                                )
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                            ]
                        ),
                        ft.Row(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(height=1, bgcolor="#00000000", width=400, margin=Margin(0, 45, 0, 40))
                            ]
                        ),

                    ]
                ),
                ft.Container(
                    padding=ft.Padding(40, 0, 40, 0),
                    top=0, right=0,
                    content=ft.FloatingActionButton(bgcolor='#d13288', icon=ft.icons.SYNC, width=50,
                                                    height=50, on_click=self.on_synchronize_click),
                )
            ])

    def on_visitor_created_click(self, e):
        try:
            visitor_id = self.visitor_id_field.value
            is_authenticated = self.authenticated_switch.value
            has_consented = self.consent_switch.value
            context = json.loads(self.context_field.value)
            self.visitor = Flagship.new_visitor(visitor_id, authenticated=is_authenticated, consent=has_consented,
                                                context=context, instance_type=Visitor.Instance.NEW_INSTANCE)
            self.update_visitor_front()
            self.visitor.fetch_flags()
            self.save_visitor_in_cache()
            self.on_visitor_synchronized(self.visitor)
        except Exception as e:
            print(traceback.print_exc())

    def on_update_context_click(self, e):
        try:
            if self.visitor is not None:
                self.visitor.update_context(json.loads(self.update_context_field.value))
                self.update_visitor_front()
                self.visitor.fetch_flags()
        except Exception as e:
            print(traceback.print_exc())

    def on_authenticate_click(self, e):
        try:
            self.visitor.authenticate(self.authenticate_field.value)
            self.update_visitor_front()
            self.visitor.fetch_flags()
        except Exception as e:
            print(traceback.print_exc())

    def on_unauthenticate_click(self, e):
        try:
            if self.visitor is not None:
                self.visitor.unauthenticate()
                self.update_visitor_front()
                self.visitor.fetch_flags()
        except Exception as e:
            print(traceback.print_exc())

    def on_consent_changed(self, e):
        try:
            print("CHANGED CONSENT BUT VISITOR IS NONE : " + str(self.update_consent_switch.value))
            if self.visitor is not None:
                print("CHANGED CONSENT : " + str(self.update_consent_switch.value))
                self.visitor.set_consent(self.update_consent_switch.value)
                self.update_visitor_front()
                self.visitor.fetch_flags()
        except Exception as e:
            print(traceback.print_exc())

    def on_synchronize_click(self, e):
        try:
            if self.visitor is not None:
                self.visitor.fetch_flags()
                self.save_visitor_in_cache()
        except Exception as e:
            print(traceback.print_exc())

    def update_visitor_front(self):
        if self.visitor is not None:
            self.visitor_id_field.value = self.visitor.visitor_id
            self.anonymous_id_field.value = self.visitor.anonymous_id if self.visitor.anonymous_id is not None else ""
            self.authenticated_switch.value = self.visitor.is_authenticated
            self.consent_switch.value = self.visitor.has_consented
            self.context_field.value = pretty_dict(self.visitor.context)
            self.update_context_field.value = pretty_dict(self.visitor.context)
            self.update_consent_switch.value = self.visitor.has_consented
            self.update()
            self.on_visitor_synchronized(self.visitor)

    def save_visitor_in_cache(self):
        if self.visitor is not None:
            self.page.client_storage.remove("visitor_id_field")
            self.page.client_storage.remove("anonymous_id_field")
            self.page.client_storage.remove("consent_switch")
            self.page.client_storage.remove("authenticated_switch")
            self.page.client_storage.remove("context_field")
            if self.visitor_id_field.value is not None:
                self.page.client_storage.set("visitor_id_field", self.visitor_id_field.value)
            if self.anonymous_id_field.value is not None:
                self.page.client_storage.set("anonymous_id_field", self.anonymous_id_field.value)
            if self.authenticated_switch.value is not None:
                self.page.client_storage.set("authenticated_switch", self.authenticated_switch.value)
            if self.consent_switch.value is not None:
                self.page.client_storage.set("consent_switch", self.consent_switch.value)
            if self.context_field.value is not None:
                self.page.client_storage.set("context_field", self.context_field.value)

    def load_visitor_from_cache(self):

        if self.page.client_storage.contains_key("visitor_id_field"):
            self.visitor_id_field.value = self.page.client_storage.get("visitor_id_field")
        if self.page.client_storage.contains_key("anonymous_id_field"):
            self.anonymous_id_field.value = self.page.client_storage.get("anonymous_id_field")
        if self.page.client_storage.contains_key("authenticated_switch"):
            self.authenticated_switch.value = self.page.client_storage.get("authenticated_switch")
        if self.page.client_storage.contains_key("consent_switch"):
            self.consent_switch.value = self.page.client_storage.get("consent_switch")
        if self.page.client_storage.contains_key("context_field"):
            self.context_field.value = self.page.client_storage.get("context_field")


class FlagView(ft.Container):
    def __init__(self, page: Page, visitor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.visitor = visitor
        self.flag_listview = ft.ListView(spacing=20, auto_scroll=True, padding=20)
        self.flag_key_field = ft.TextField(border_color='#919993', label="Flag key")
        self.flag_default_field = ft.TextField(border_color='#919993', label="Flag default value", multiline=True,
                                               max_lines=1)
        self.flag_default_type_dropdown = ft.Dropdown(border_color='#919993', width=300,
                                                      options=[ft.dropdown.Option("str"),
                                                               ft.dropdown.Option("int"),
                                                               ft.dropdown.Option("float"),
                                                               ft.dropdown.Option("bool"),
                                                               ft.dropdown.Option("dict"),
                                                               # ft.dropdown.Option("array"),
                                                               ],
                                                      value="str")
        ###
        self.get_flag_key_textview = ft.Text("Key: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993', width=300,
                                             selectable=True)
        self.get_flag_value_textview = ft.Text("Value: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993', width=300,
                                               selectable=True)
        self.get_flag_default_textview = ft.Text("Default: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                                 width=300, selectable=True)
        self.get_flag_exists_textview = ft.Text("Exists: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                                width=300, selectable=True)
        self.metadata_campaign_id_textview = ft.Text("C. id: ", style=TextThemeStyle.TITLE_MEDIUM,
                                                     color='#919993', width=300, selectable=True)
        self.metadata_group_id_textview = ft.Text("VG. id: ", style=TextThemeStyle.TITLE_MEDIUM,
                                                  color='#919993',
                                                  width=300, selectable=True)
        self.metadata_variation_id_textview = ft.Text("V. id: ", style=TextThemeStyle.TITLE_MEDIUM,
                                                      color='#919993', width=300, selectable=True)
        self.metadata_type_textview = ft.Text("Type: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                              width=300, selectable=True)
        self.metadata_slug_textview = ft.Text("Slug: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                              width=300, selectable=True)
        self.metadata_reference_textview = ft.Text("Reference: ", style=TextThemeStyle.TITLE_MEDIUM, color='#919993',
                                                   width=300, selectable=True)
        ###
        self.content = ft.Column(
            spacing=20,
            scroll=ScrollMode.ALWAYS,
            controls=[
                ft.Container(
                    padding=ft.Padding(0, 0, 0, 20),
                    content=ft.Text("Flags", style=TextThemeStyle.TITLE_LARGE, color='#FF8974')
                ),
                ft.Row(
                    alignment=MainAxisAlignment.START,
                    controls=[
                        self.flag_key_field,
                        self.flag_default_field,
                        self.flag_default_type_dropdown,
                    ]
                ),
                ft.Container(
                    padding=ft.Padding(0, 20, 100, 0),
                    content=ft.Row(
                        alignment=MainAxisAlignment.START,
                        controls=[
                            ft.FilledButton(text="Get", style=ButtonStyle(overlay_color="#d13288"), width=100,
                                            on_click=self.on_flag_get),
                            ft.FilledButton(text="Expose", style=ButtonStyle(overlay_color="#d13288"), width=100,
                                            on_click=self.on_flag_exposed)
                        ]
                    ),
                ),
                ft.Container(
                    padding=ft.Padding(0, 20, 100, 0),
                    content=ft.Row(
                        alignment=MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        spacing=20,
                        controls=[
                            ft.Column(
                                controls=[
                                    self.get_flag_key_textview,
                                    self.get_flag_value_textview,
                                    self.get_flag_default_textview,
                                    self.get_flag_exists_textview
                                ]
                            ),
                            ft.Column(
                                alignment=MainAxisAlignment.START,
                                controls=[
                                    self.metadata_campaign_id_textview,
                                    self.metadata_group_id_textview,
                                    self.metadata_variation_id_textview,
                                ]
                            ),
                            ft.Column(
                                alignment=MainAxisAlignment.START,
                                controls=[
                                    self.metadata_type_textview,
                                    self.metadata_slug_textview,
                                    self.metadata_reference_textview
                                ]
                            )
                        ], )
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                    ]
                ),
                self.flag_listview
            ]
        )
        self.on_content_displayed(True)

    def get_flag_from_flagship(self):
        if self.visitor is not None:
            try:
                key = self.flag_key_field.value
                default = self.flag_default_field.value
                default_type = self.flag_default_type_dropdown.value
                if default is not None:
                    if default_type == "int":
                        flag = self.visitor.get_flag(key, int(default))
                    elif default_type == "float":
                        flag = self.visitor.get_flag(key, float(default))
                    elif default_type == "bool":
                        flag = self.visitor.get_flag(key, bool(default.capitalize()))
                    elif default_type == "dict":
                        flag = self.visitor.get_flag(key, json.loads(default))
                    else:
                        flag = self.visitor.get_flag(key, str(default_type))
                    return flag
            except ValueError as e:
                print(traceback.print_exc())
        return None

    def on_flag_get(self, e):
        flag = self.get_flag_from_flagship()
        if flag is not None:
            self.update_flag_view(flag)

    def update_flag_view(self, flag: Flag):

        self.get_flag_key_textview.value = "Key: " + flag.key
        self.get_flag_value_textview.value = "Value: " + str(flag.value(False))
        self.get_flag_default_textview.value = "Default: " + str(flag.default_value)
        self.get_flag_exists_textview.value = "Exists: " + str(flag.exists())
        metadata = flag.metadata()
        self.metadata_campaign_id_textview.value = "C. id: " + metadata.campaign_id
        self.metadata_group_id_textview.value = "VG. id: " + metadata.variation_group_id
        self.metadata_variation_id_textview.value = "V. id: " + metadata.variation_id
        self.metadata_type_textview.value = "Type: " + str(metadata.campaign_type)
        self.metadata_slug_textview.value = "Slug: " + str(metadata.campaign_slug)
        self.metadata_reference_textview.value = "Reference: " + str(metadata.is_reference)
        self.update()

    def on_flag_exposed(self, e):
        flag: Flag = self.get_flag_from_flagship()
        if flag is not None:
            flag.user_exposed()

    def on_visitor_synchronized(self, new_visitor: Visitor):
        if new_visitor is not None:
            self.visitor = new_visitor

    def on_content_displayed(self, init=False):
        if self.visitor is not None:
            # self.flag_listview.controls.clear()
            for k, v in self.visitor._modifications.items():
                t = "'{}'= {}".format(k, v.value)
                self.flag_listview.controls.append(
                    ft.Text(t, style=TextThemeStyle.TITLE_SMALL, color='#FF8974', selectable=True)
                )
            # if not init:
            #     self.flag_listview.update()


class HitView(ft.Container):
    def __init__(self, page: Page, visitor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.visitor = visitor
        self.screen_name_textfield = ft.TextField(border_color='#919993', label="Interface name", width=300)
        self.page_name_textfield = ft.TextField(border_color='#919993', label="Page url", width=300)
        self.event_action_textfield = ft.TextField(border_color='#919993', label="Event Action", width=300)
        self.event_category_dropdown = ft.Dropdown(border_color='#919993', width=300,
                                                   options=[ft.dropdown.Option("User engagement"),
                                                            ft.dropdown.Option("Action tracking"),
                                                            ],
                                                   value="User engagement")
        self.transaction_id_textfield = ft.TextField(border_color='#919993', label="Transaction id", width=300)
        self.transaction_affiliation_textfield = ft.TextField(border_color='#919993', label="Affiliation", width=300)
        self.item_transaction_id_textfield = ft.TextField(border_color='#919993', label="Transaction id", width=300)
        self.item_name_textfield = ft.TextField(border_color='#919993', label="Name", width=300)
        self.item_sku_textfield = ft.TextField(border_color='#919993', label="SKU", width=300)
        self.content = ft.Column(
            spacing=20,
            scroll=ScrollMode.ALWAYS,
            controls=[
                ft.Container(
                    padding=ft.Padding(0, 0, 0, 20),
                    content=ft.Text("Hits", style=TextThemeStyle.TITLE_LARGE, color='#FF8974')
                ),
                # Screen
                ft.Container(
                    alignment=Alignment(0, 0),
                    padding=ft.Padding(0, 0, 0, 20),
                    content=ft.Text("Screen", style=TextThemeStyle.TITLE_SMALL, color='#FF8974')
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.screen_name_textfield
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.FilledButton(text="Send", style=ButtonStyle(overlay_color="#d13288"), width=100,
                                        on_click=self.on_fire_screen),
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                    ]
                ),
                # Page
                ft.Container(
                    alignment=Alignment(0, 0),
                    padding=ft.Padding(0, 0, 0, 20),
                    content=ft.Text("Page", style=TextThemeStyle.TITLE_SMALL, color='#FF8974')
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.page_name_textfield
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.FilledButton(text="Send", style=ButtonStyle(overlay_color="#d13288"), width=100,
                                        on_click=self.on_fire_page),
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                    ]
                ),
                # Event
                ft.Container(
                    alignment=Alignment(0, 0),
                    padding=ft.Padding(0, 0, 0, 20),
                    content=ft.Text("Event", style=TextThemeStyle.TITLE_SMALL, color='#FF8974')
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.event_category_dropdown
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.event_action_textfield
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.FilledButton(text="Send", style=ButtonStyle(overlay_color="#d13288"), width=100,
                                        on_click=self.on_fire_event),
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                    ]
                ),
                # Transaction
                ft.Container(
                    alignment=Alignment(0, 0),
                    padding=ft.Padding(0, 0, 0, 20),
                    content=ft.Text("Transaction", style=TextThemeStyle.TITLE_SMALL, color='#FF8974')
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.transaction_id_textfield
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.transaction_affiliation_textfield
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.FilledButton(text="Send", style=ButtonStyle(overlay_color="#d13288"), width=100,
                                        on_click=self.on_fire_transaction),
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                    ]
                ),
                # Item
                ft.Container(
                    alignment=Alignment(0, 0),
                    padding=ft.Padding(0, 0, 0, 20),
                    content=ft.Text("Item", style=TextThemeStyle.TITLE_SMALL, color='#FF8974')
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.item_transaction_id_textfield
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.item_name_textfield
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        self.item_sku_textfield
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.FilledButton(text="Send", style=ButtonStyle(overlay_color="#d13288"), width=100,
                                        on_click=self.on_fire_item),
                    ]
                ),
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(height=1, bgcolor="#d13288", width=400, margin=Margin(0, 45, 0, 40))
                    ]
                ),
            ]
        )

    def on_fire_screen(self, e):
        if self.visitor is not None:
            self.visitor.send_hit(Screen(self.screen_name_textfield.value))

    def on_fire_page(self, e):
        if self.visitor is not None:
            self.visitor.send_hit(flagship.hits.Page(self.page_name_textfield.value))

    def on_fire_event(self, e):
        if self.visitor is not None:
            self.visitor.send_hit(Event(
                EventCategory.USER_ENGAGEMENT if self.event_category_dropdown.value == "User engagement"
                else EventCategory.ACTION_TRACKING,
                self.event_action_textfield.value))

    def on_fire_transaction(self, e):
        if self.visitor is not None:
            self.visitor.send_hit(Transaction(self.transaction_id_textfield.value,
                                              self.transaction_affiliation_textfield.value))

    def on_fire_item(self, e):
        if self.visitor is not None:
            self.visitor.send_hit(Item(self.item_transaction_id_textfield.value,
                                       self.item_name_textfield.value,
                                       self.item_sku_textfield.value))


class Content(ft.Container):

    def __init__(self, page: Page, log_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_manager = log_manager
        self.page = page
        self.index = 0
        self.visitor = None
        self.current_view = None
        # self.current_view = self.build_view()
        # self.content = self.current_view
        self.on_page_changed(self.index, init=True)



    def on_page_changed(self, index, init=False):
        self.index = index
        self.current_view = self.build_view()
        self.content = self.current_view
        # if isinstance(self.current_view, ConfigurationView):
        #     self.current_view.on_content_displayed(init)
        # elif isinstance(self.current_view, FlagView):
        #     self.current_view.on_content_displayed(init)
        if not init:
            self.update()

    def on_visitor_synchronized(self, visitor):
        if visitor is not None:
            self.visitor = visitor

    def build_view(self):
        try:
            if self.index == 0:
                configuration_view = ConfigurationView(self.page, self.log_manager)
                configuration_view.padding = ft.Padding(20, 0, 0, 0)
                return configuration_view
            elif self.index == 1:
                visitor = self.visitor if self.visitor is not None else None
                visitor_view = VisitorView(self.page, visitor, self.on_visitor_synchronized)
                visitor_view.padding = ft.Padding(20, 0, 0, 0)
                return visitor_view
            elif self.index == 2:
                visitor = self.visitor if self.visitor is not None else None
                flag_view = FlagView(self.page, visitor)
                flag_view.padding = ft.Padding(20, 0, 0, 0)
                return flag_view
            elif self.index == 3:
                visitor = self.visitor if self.visitor is not None else None
                hit_view = HitView(self.page, visitor)
                hit_view.padding = ft.Padding(20, 0, 0, 0)
                return hit_view
        except Exception as e:
            print(traceback.print_exc())
        return None


class LogView(ft.Container):

    def __init__(self, page: Page, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_view = ft.ListView(spacing=10, auto_scroll=True, padding=20)
        self.padding = ft.Padding(20, 0, 0, 20)
        self.content = ft.Stack(
            controls=[
                ft.Column(
                    auto_scroll=True,
                    scroll=ScrollMode.ALWAYS,
                    controls=[
                        ft.Text("SDK logs", style=TextThemeStyle.TITLE_LARGE, color='#FF8974'),
                        self.log_view
                    ]),
                ft.Container(
                    padding=ft.Padding(40, 0, 40, 0),
                    top=0, right=0,
                    content=ft.FloatingActionButton(bgcolor='#d13288', icon=ft.icons.CLEAR_ALL, width=50,
                                                    height=50, on_click=self.on_clear_logs),
                )
            ]
        )

    def on_clear_logs(self, e):
        self.log_view.controls.clear()
        self.log_view.update()

    def log(self, tag, level, message):
        if level == LogLevel.ERROR:
            color = '#FF0000'
        elif level == LogLevel.WARNING:
            color = '#FFFF00'
        elif level == LogLevel.INFO:
            color = '#1FAFDE'
        else:
            color = '#919993'
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.log_view.controls.append(
            ft.Text("[{}][{}][{}]: {}".format(
                now, tag, str(level), message
            ), color=color, selectable=True))
        self.log_view.update()


class QAApp(ft.UserControl):

    def __init__(self, page: Page):
        super().__init__()

        self.page = page
        self.log_view = LogView(page, expand=3, padding=20)
        self.custom_log_manager = CustomLogManager(self.log_view.log)
        self.sidebar = SideBar(page, self.on_page_changed)
        self.content = Content(page, self.custom_log_manager, expand=5)
        # self.log_view = ft.ListView(expand=3, spacing=10, padding=20, auto_scroll=True)

    def on_page_changed(self, index):
        self.content.on_page_changed(index)

    def build(self):
        return ft.Column(
            controls=[
                ft.Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=ft.Padding(20, 20, 20, 40),
                            content=ft.Text("Flagship Python QA app", style=TextThemeStyle.TITLE_LARGE, color='#d13288')
                        )
                    ]
                ),
                ft.Row(
                    expand=True,
                    alignment=MainAxisAlignment.START,
                    vertical_alignment=CrossAxisAlignment.START,
                    controls=[
                        self.sidebar,
                        ft.VerticalDivider(width=5, color="#d13288"),
                        self.content,
                        ft.VerticalDivider(width=5, color="#d13288"),
                        self.log_view
                    ]
                ),
            ],
            # tight=True
        )


class CustomLogManager(LogManager):

    def __init__(self, on_log):
        self.on_log = on_log

    def log(self, tag, level, message):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print("[{}][{}][{}]: {}".format(now, tag, str(level), message))
        self.on_log(tag, level, message)

    def exception(self, tag, exception, traceback_err):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print("[{}][{}][{}]: {}".format(now, tag, str(LogLevel.ERROR), str(traceback_err)))
        # self.on_log(tag, LogLevel.ERROR, traceback_err.print_exc())


def main(page: ft.Page):
    print(sys.version)
    page.title = "QA"
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.theme_mode = ThemeMode.DARK
    app = QAApp(page)
    app.expand = True
    page.add(app)
    page.update()


# import logging
# logging.basicConfig(level=logging.DEBUG)
ft.app(name="QA APP", target=main, view=ft.WEB_BROWSER, port=8550)
