import json


class MockTeamsAPI:
    @classmethod
    def list_webhooks(cls):
        response = {
            "items": [
                {
                    "id": "someID",
                    "name": "My Awesome Webhook",
                    "targetUrl": "https://example.com/mywebhook",
                    "resource": "messages",
                    "event": "created",
                    "filter": "roomId=someroomID",
                    "secret": "86dacc007724d8ea666f88fc77d918dad9537a15",
                    "status": "active",
                    "created": "2015-10-18T14:26:16+00:00",
                }
            ]
        }
        return response

    @classmethod
    def list_webhooks_exist(cls):
        data = MockTeamsAPI.list_webhooks()
        data["items"][0]["name"] = "testbot"
        return data

    @classmethod
    def create_webhook(cls):
        response = {
            "id": "newwebhook",
            "name": "My Awesome Webhook",
            "targetUrl": "https://example.com/mywebhook",
            "resource": "messages",
            "event": "created",
            "filter": "roomId=someRoomId",
            "secret": "86dacc007724d8ea666f88fc77d918dad9537a15",
            "status": "active",
            "created": "2015-10-18T14:26:16+00:00",
        }
        return response

    @classmethod
    def incoming_msg(cls):
        data = {
            "id": "asdfadfsadfasdf",
            "name": "New message in 'Project Unicorn' room",
            "resource": "messages",
            "event": "created",
            "filter": "roomId=sadfasdfsdffsadfd",
            "orgId": "OTZhYmMyYWEtM2RjYy0xMWU1LWExNTItZmUzNDgxOWNkYzlh",
            "createdBy": "fdsafdsf",
            "appId": "asdfasdfsadf",
            "ownedBy": "creator",
            "status": "active",
            "actorId": "asdffsdfsdsafd",
            "data": {
                "id": "incoming_message_id",
                "roomId": "some_room_id",
                "personId": "some_person_id",
                "personEmail": "matt@example.com",
                "created": "2015-10-18T14:26:16.000Z",
            },
        }
        return json.dumps(data)

    @classmethod
    def incoming_membership_fail(cls):
        data = {
            'id': 'newwebhook',
            'name': 'My Awesome Webhook',
            'targetUrl': 'https://example.com/mywebhook',
            'resource': 'memberships',
            'event': 'created',
            'orgId': 'OTZhYmMyYWEtM2RjYy0xMWU1LWExNTItZmUzNDgxOWNkYzlh',
            'createdBy': 'fdsafdsf',
            'appId': 'asdfasdfsadf',
            'ownedBy': 'creator',
            'status': 'active',
            'created': '2018-09-13T19:35:51.248Z',
            'actorId': 'OTZhYmMyYWEtM2RjYy0xMWU1LWExNTItZmUzNDgxOWNkYzlh',
            'data': {
                'id': 'incoming_membership_id',
                'roomId': 'some_room_id',
                'personId': 'some_person_id',
                'personEmail': 'matt@example.com',
                'personDisplayName': 'Matt',
                'personOrgId': 'OTZhYmMyYWEtM2RjYy0xMWU1LWExNTItZmUzNDgxOWNk',
                'isModerator': False,
                'isMonitor': False,
                'created': '2018-09-13T19:35:58.803Z'
            }
        }
        return json.dumps(data)

    @classmethod
    def incoming_membership_pass(cls):
        data = {
            'id': 'newwebhook',
            'name': 'My Awesome Webhook',
            'targetUrl': 'https://example.com/mywebhook',
            'resource': 'memberships',
            'event': 'created',
            'orgId': 'OTZhYmMyYWEtM2RjYy0xMWU1LWExNTItZmUzNDgxOWNkYzlh',
            'createdBy': 'fdsafdsf',
            'appId': 'asdfasdfsadf',
            'ownedBy': 'creator',
            'status': 'active',
            'created': '2018-09-13T19:35:51.248Z',
            'actorId': 'OTZhYmMyYWEtM2RjYy0xMWU1LWExNTItZmUzNDgxOWNkYzlh',
            'data': {
                'id': 'incoming_membership_id',
                'roomId': 'some_room_id',
                'personId': 'some_person_id',
                'personEmail': 'matt@cisco.com',
                'personDisplayName': 'Matt',
                'personOrgId': 'OTZhYmMyYWEtM2RjYy0xMWU1LWExNTItZmUzNDgxOWNk',
                'isModerator': False,
                'isMonitor': False,
                'created': '2018-09-13T19:35:58.803Z'
            }
        }
        return json.dumps(data)

    @classmethod
    def get_message_help(cls):
        data = {
            "id": "some_message_id",
            "roomId": "some_room_id",
            "roomType": "group",
            "toPersonId": "some_person_id",
            "toPersonEmail": "julie@example.com",
            "text": "/help",
            "personEmail": "matt@example.com",
            "personId": "some_person_id",
            "created": "2015-10-18T14:26:16+00:00",
        }
        return data

    # @classmethod
    # def get_message_echo(cls):
    #     data = MockTeamsAPI.get_message_help()
    #     data['text'] = "/echo foo"
    #     return data

    @classmethod
    def empty_message(cls):
        data = MockTeamsAPI.get_message_help()
        data["text"] = ""
        return data

    @classmethod
    def get_message_dosomething(cls):
        data = MockTeamsAPI.get_message_help()
        data["text"] = "/echo imtheecho"
        return data

    @classmethod
    def get_message_from_bot(cls):
        data = MockTeamsAPI.get_message_help()
        data["personEmail"] = "foo@foo.com"
        return data

    @classmethod
    def me(cls):
        data = {
            "id": "myid",
            "emails": ["foo@foo.com"],
            "displayName": "Some User",
            "nickName": "SomeUser",
            "firstName": "Some",
            "lastName": "User",
            "avatar": "https://some-avatar-url.com/sdflkjsdflkajs",
            "orgId": "orgid",
            "created": "2012-06-15T20:32:02.438Z",
            "lastActivity": "2018-04-09T21:15:44.677Z",
            "status": "inactive",
            "type": "person",
        }
        return data
