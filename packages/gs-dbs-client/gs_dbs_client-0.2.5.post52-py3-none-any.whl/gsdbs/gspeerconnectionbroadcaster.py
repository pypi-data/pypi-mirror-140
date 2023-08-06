import ast
import json
import logging
import platform
import time

import socketio
from aiortc import RTCPeerConnection
from aiortc.contrib.media import MediaPlayer, MediaRelay


class GSPeerConnectionBroadcaster:

    def create_local_tracks(self, fr, hres, vres, rtbufsize):
        options = {"framerate": str(fr), "video_size": str(hres) + "x" + str(vres), "rtbufsize": str(rtbufsize)}
        relay = MediaRelay()
        if platform.system() == "Darwin":
            webcam = MediaPlayer("default:none", format="avfoundation", options=options)
        elif platform.system() == "Windows":
            webcam = MediaPlayer("video=HD 720P Webcam", format="dshow", options=options)
        else:
            webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)

        return relay.subscribe(webcam.video)

    @classmethod
    async def create(cls, gsdbs):
        self = GSPeerConnectionBroadcaster()
        self.gsdbs = gsdbs
        self.sio = socketio.AsyncClient()
        self.peerConnections = {}
        self._logger = logging.getLogger(__name__)

        @self.sio.event
        async def connect():
            self._logger.info('connection established')
            await self.sio.emit("broadcaster", "")

        @self.sio.event
        async def answer(id, description):
            if type(description) == str:
                description = ast.literal_eval(description)
            desc = type('new_dict', (object,), description)
            time.sleep(0.5)
            await self.peerConnections[id].setRemoteDescription(desc)

        @self.sio.event
        async def watcher(id):
            pc = RTCPeerConnection()
            self.peerConnections[id] = pc
            video = self.create_local_tracks(
                self.gsdbs.credentials["framerate"],
                self.gsdbs.credentials["hres"],
                self.gsdbs.credentials["vres"],
                self.gsdbs.credentials["rtbufsize"]
            )
            pc.addTrack(video)
            channel = pc.createDataChannel("message")

            # def send_data():
            #     channel.send("test123")
            #
            # channel.on("open", send_data)

            await pc.setLocalDescription(await pc.createOffer())
            await self.sio.emit("offer", {"id": id,
                                          "message": json.dumps(
                                              {"type": pc.localDescription.type, "sdp": pc.localDescription.sdp})})
            self._logger.info(pc.signalingState)

        @self.sio.event
        async def disconnectPeer(id):
            await self.peerConnections[id].close()
            self._logger.info(self.peerConnections[id].signalingState)

        @self.sio.event
        async def disconnect():
            self._logger.info('disconnected from server')

        await self.sio.connect(
            f'{self.gsdbs.credentials["signalserver"]}:{str(self.gsdbs.credentials["signalport"])}?gssession={self.gsdbs.cookiejar.get("session")}.{self.gsdbs.cookiejar.get("signature")}{self.gsdbs.credentials["cnode"]}')
        await self.sio.wait()
