

class User(object):
    '''Contains a collection of user related asynchron methods.'''

    async def get_current_user(self) -> dict:
        '''https://discord.com/developers/docs/resources/user#get-current-user'''
        return await self._request(method='GET', uri=f'/users/@me')

    async def get_user(self, user_id) -> dict:
        '''https://discord.com/developers/docs/resources/user#get-user'''
        return await  self._request(method='GET', uri=f'/users/{user_id}')

    async def modify_current_user(self, username: str=None, avatar=None) -> dict:
        '''https://discord.com/developers/docs/resources/user#modify-current-user'''
        payload: dict = { 'username': username, 'avatar': avatar}
        payload: dict = {k:v for k,v in payload.items() if v is not None}
        return await  self._request(method='PATCH', params=payload, uri=f'/users/@me')

    async def get_current_user_guilds(self, before=None, after=None, limit: int=None) -> dict:
        '''https://discord.com/developers/docs/resources/user#get-current-user-guilds'''
        payload: dict = { 
            'before': before,
            'after': after,
            'limit': limit,
        }
        payload: dict = {k:v for k,v in payload.items() if v is not None}
        return await  self._request(method='GET', params=payload, uri=f'/users/@me/guilds')

    async def get_current_user_guild_member(self, guild_id) -> dict:
        '''https://discord.com/developers/docs/resources/user#get-current-user-guild-member'''
        return await  self._request(method='GET', uri=f'/users/@me/guilds/{guild_id}/member')

    async def leave_guild(self, guild_id) -> dict:
        '''https://discord.com/developers/docs/resources/user#leave-guild'''
        return await  self._request(method='DELETE', uri=f'/users/@me/guilds/{guild_id}')

    async def create_dm(self, recipient_id) -> dict:
        '''https://discord.com/developers/docs/resources/user#create-dm'''
        payload: dict = { 'recipient_id': recipient_id }
        return await  self._request(method='POST', params=payload, uri=f'/users/@me/channels')

    async def create_group_dm(self, access_tokens: list, nicks: dict) -> dict:
        '''https://discord.com/developers/docs/resources/user#create-group-dm'''
        payload: dict = {
            'access_tokens': access_tokens,
            'nicks': nicks
        }
        return await  self._request(method='POST', params=payload, uri=f'/users/@me/channels')

    async def get_user_connections(self) -> dict:
        '''https://discord.com/developers/docs/resources/user#get-user-connections'''
        return await  self._request(method='GET', uri=f'/users/@me/connections')

    async def list_voice_regions(self) -> dict:
        '''https://discord.com/developers/docs/resources/voice#list-voice-regions'''
        return await  self._request(method='GET', uri=f'/voice/regions')

    async def get_invite(self, invite_code, with_counts: bool=None, with_expiration: bool=None, guild_scheduled_event_id=None) -> dict:
        '''https://discord.com/developers/docs/resources/invite#get-invite'''
        payload: dict = {
            'with_counts': with_counts,
            'with_expiration': with_expiration,
            'guild_scheduled_event_id': guild_scheduled_event_id
        }
        payload: dict = {k:v for k,v in payload.items() if v is not None}
        return await  self._request(method='GET', params=payload, uri=f'/invites/{invite_code}')

    async def delete_invite(self, invite_code) -> dict:
        '''https://discord.com/developers/docs/resources/invite#delete-invite'''
        return await  self._request(method='DELETE', params=payload, uri=f'/invites/{invite_code}')



    