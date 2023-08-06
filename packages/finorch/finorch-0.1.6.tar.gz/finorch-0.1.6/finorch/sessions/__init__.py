from finorch.sessions.cit import CitSession
from finorch.sessions.local import LocalSession
from finorch.sessions.ozstar import OzStarSession
from finorch.sessions.ssh import SshSession

session_map = {
    LocalSession.callsign: LocalSession,
    OzStarSession.callsign: OzStarSession,
    CitSession.callsign: CitSession,
    SshSession.callsign: SshSession
}
