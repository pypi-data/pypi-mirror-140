class Nandbox:
    class Callback:
        def on_connect(self, api):
            pass

        def on_receive(self, incoming_msg):
            pass

        def on_receive_obj(self, obj):
            pass

        def on_close(self):
            pass

        def on_error(self):
            pass

        def on_chat_menu_callback(self, chat_menu_callback):
            pass

        def on_inline_message_callback(self, inline_msg_callback):
            pass

        def on_message_ack_callback(self, msg_ack):
            pass

        def on_user_joined_bot(self, user):
            pass

        def on_chat_member(self, chat_member):
            pass

        def on_chat_administrators(self, chat_administrators):
            pass

        def user_started_bot(self, user):
            pass

        def on_my_profile(self, user):
            pass

        def on_user_details(self, user):
            pass

        def user_stopped_bot(self, user):
            pass

        def user_left_bot(self, user):
            pass

        def permanent_url(self, url):
            pass

        def on_chat_details(self, chat):
            pass

        def on_inline_search(self, inline_search):
            pass

        def on_black_list(self, black_list):
            pass

        def on_white_list(self, white_list):
            pass

        def on_schedule_message(self, incoming_schedule_msg):
            pass

    class Api:
        def send(self, message):
            pass

        def send_text_with_background(self, chat_id, text, bg_color):
            pass

        def send_text(self, chat_id, text, reference, reply_to_message_id=None, to_user_id=None, web_page_preview=None,
                      disable_notification=None, chat_settings=None, bg_color=None, tab=None):
            pass

        def send_photo(self, chat_id, photo_file_id, reference, reply_to_message_id=None, to_user_id=None, web_page_preview=None,
                       disable_notification=None, caption=None, chat_settings=None, tab=None):
            pass

        def send_video(self, chat_id, video_file_id, reference, reply_to_message_id=None, to_user_id=None, web_page_preview=None,
                       disable_notification=None, caption=None, chat_settings=None, tab=None):
            pass

        def send_audio(self, chat_id, audio_file_id, reference, reply_to_message_id=None, to_user_id=None, web_page_preview=None,
                       disable_notification=None, caption=None, performer=None, title=None, chat_settings=None, tab=None):
            pass

        def send_contact(self, chat_id, phone_number, name, reference, reply_to_message_id=None, to_user_id=None,
                         web_page_preview=None, disable_notification=None, chat_settings=None, tab=None):
            pass

        def send_voice(self, chat_id, voice_file_id, reference, reply_to_message_id=None, to_user_id=None, web_page_preview=None,
                       disable_notification=None, caption=None, size=None, chat_settings=None, tab=None):
            pass

        def send_document(self, chat_id, document_file_id, reference, reply_to_message_id=None, to_user_id=None, web_page_preview=None,
                          disable_notification=None, caption=None, name=None, size=None, chat_settings=None, tab=None):
            pass

        def send_location(self, chat_id, latitude, longitude, reference, reply_to_message_id=None, to_user_id=None,
                          web_page_preview=None, disable_notification=None, name=None, details=None, chat_settings=None, tab=None):
            pass

        def send_gif(self, chat_id, gif_file_id, reference, reply_to_message_id=None, to_user_id=None, web_page_preview=None,
                     disable_notification=None, caption=None, chat_settings=None, tab=None):
            pass

        def send_gif_video(self, chat_id, gif_file_id, reference, reply_to_message_id=None, to_user_id=None, web_page_preview=None,
                           disable_notification=None, caption=None, chat_settings=None, tab=None):
            pass

        def update_message(self, message_id, text=None, caption=None, to_user_id=None, chat_id=None, tab=None):
            pass

        def update_text_msg(self, message_id, text, to_user_id, tab):
            pass

        def update_media_caption(self, message_id, caption, to_user_id, tab):
            pass

        def update_chat_msg(self, message_id, text, chat_id, tab):
            pass

        def update_chat_media_caption(self, message_id, caption, chat_id, tab):
            pass

        def get_user(self, user_id):
            pass

        def get_chat(self, chat_id):
            pass

        def get_chat_member(self, chat_id, user_id):
            pass

        def get_chat_administrators(self, chat_id):
            pass

        def ban_chat_member(self, chat_id, user_id):
            pass

        def unban_chat_member(self, chat_id, user_id):
            pass

        def remove_chat_member(self, chat_id, user_id):
            pass

        def recall_message(self, chat_id, message_id, to_user_id, reference):
            pass

        def set_my_profile(self, user):
            pass

        def set_chat(self, chat):
            pass

        def get_my_profiles(self):
            pass

        def generate_permanent_url(self, file, param1):
            pass

        def get_black_list(self, chat_id):
            pass

        def get_white_list(self, chat_id):
            pass

        def add_black_list(self, chat_id, users):
            pass

        def add_white_list(self, chat_id, white_list_users):
            pass

        def delete_black_list(self, chat_id, users):
            pass

        def delete_white_list(self, chat_id, users):
            pass

        def add_black_list_patterns(self, chat_id, data):
            pass

        def add_white_list_patterns(self, chat_id, data):
            pass

        def delete_black_list_patterns(self, chat_id, pattern):
            pass

        def delete_white_list_patterns(self, chat_id, pattern):
            pass
