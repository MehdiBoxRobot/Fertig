from pyrogram.errors import UserNotParticipant
from config import CHANNELS

async def check_user_subscriptions(client, user_id):
    for channel in CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False, channel
        except UserNotParticipant:
            return False, channel
        except Exception:
            return False, channel
    return True, None
