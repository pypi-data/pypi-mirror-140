import ast
import json
import socketio
from aiortc import MediaStreamTrack, RTCPeerConnection


class GSPeerConnectionWatcher:
    class VideoTransformTrack(MediaStreamTrack):
        kind = "video"

        def __init__(self, track, onframe):
            super().__init__()
            self.track = track
            self.onframe = onframe

        async def recv(self):
            frame = await self.track.recv()
            self.onframe(frame)
            return frame

    @classmethod
    async def create(cls, gsdbs,target, onframe, onmessage):
        self = GSPeerConnectionWatcher()
        self.sio = socketio.AsyncClient()
        self.gsdbs=gsdbs
        self.onframe = onframe
        self.target = target
        self.onmessage = onmessage

        @self.sio.event
        async def connect():
            print('connection established')
            await self.sio.emit("watcher",  {"target": self.target})

        @self.sio.event
        async def broadcaster():
            await self.sio.emit("watcher", "")

        @self.sio.event
        async def offer(id, description):
            self.peerConnections = RTCPeerConnection()

            @self.peerConnections.on("datachannel")
            def on_datachannel(channel):
                @channel.on("message")
                def on_message(message):
                    self.onmessage(message)

            @self.peerConnections.on("iceconnectionstatechange")
            async def on_iceconnectionstatechange():
                if self.peerConnections.iceConnectionState == "failed":
                    await self.peerConnections.close()

            @self.peerConnections.on("track")
            def on_track(track):
                if track.kind == "video":
                    local_video = self.VideoTransformTrack(track, onframe=self.onframe)
                    self.peerConnections.addTrack(local_video)

                @track.on("ended")
                async def on_ended():
                    pass
                    # await recorder.stop()

            desc = type('new_dict', (object,), ast.literal_eval(description))
            await self.peerConnections.setRemoteDescription(desc)

            answer = await self.peerConnections.createAnswer()
            await self.peerConnections.setLocalDescription(answer)
            await self.sio.emit("answer", {"id": id,
                                           "message": json.dumps(
                                               {"type": self.peerConnections.localDescription.type,
                                                "sdp": self.peerConnections.localDescription.sdp})})

        await self.sio.connect(
            f'{self.gsdbs.credentials["signalserver"]}:{str(self.gsdbs.credentials["signalport"])}?gssession={self.gsdbs.cookiejar.get("session")}.{self.gsdbs.cookiejar.get("signature")}{self.gsdbs.credentials["cnode"]}')
        await self.sio.wait()