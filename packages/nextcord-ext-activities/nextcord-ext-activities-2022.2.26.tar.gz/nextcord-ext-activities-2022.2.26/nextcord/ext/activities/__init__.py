import nextcord
from .enums import Activity

import warnings

__all__ = ("Activity")
__version__ = "2022.02.26"


async def create_activity_invite_link(self, activity: Activity, activity_id: int = None) -> str:  # noqa: E501
    """
    Creates an invite link for the specified activity.

    Parameters
    -----------
    activity
        The activity to create an invite link for.
        If the value is ``Activity.custom`` and you don't pass the ``activity_id`` parameter, this will lead to an exception.
    activity_id
        The ID of the activity to create an invite link for, if ``activity`` parameter is ``Activity.custom``.
        If ``activity`` is not ``Activity.custom``, this parameter is ignored.

    Returns
    --------
        The invite link to launch the specific activity.

    Return type
    ------------
        :class:`str`
    """

    async def _create_normal_invite_link(activity_id: int):
        return await self.create_invite(
            target_type=nextcord.InviteTarget.embedded_application,
            target_application_id=activity_id
        )

    if activity == Activity.poker:
        return await _create_normal_invite_link(755827207812677713)
    elif activity == Activity.betrayal:
        return await _create_normal_invite_link(773336526917861400)
    elif activity == Activity.fishington:
        return await _create_normal_invite_link(814288819477020702)
    elif activity == Activity.chess:
        return await _create_normal_invite_link(832012774040141894)
    elif activity == Activity.checker:
        return await _create_normal_invite_link(832013003968348200)
    elif activity == Activity.ocho:
        return await _create_normal_invite_link(832025144389533716)
    elif activity == Activity.youtube:
        return await _create_normal_invite_link(880218394199220334)
    elif activity == Activity.doodle:
        warnings.warn("Doodle Crew is an old activity, and will be removed in a future release.", DeprecationWarning)  # noqa: E501
        return await _create_normal_invite_link(878067389634314250)
    elif activity == Activity.letter_tile:
        warnings.warn("letter_tile name is now deprecated, use letter_league instead.", DeprecationWarning)  # noqa: E501
        return await _create_normal_invite_link(879863686565621790)
    elif activity == Activity.letter_league:
        return await _create_normal_invite_link(879863686565621790)
    elif activity == Activity.word_snacks:
        return await _create_normal_invite_link(879863976006127627)
    elif activity == Activity.sketch:
        return await _create_normal_invite_link(902271654783242291)
    elif activity == Activity.spellcast:
        return await _create_normal_invite_link(852509694341283871)
    elif activity == Activity.awkword:
        return await _create_normal_invite_link(879863881349087252)
    elif activity == Activity.custom:
        if activity_id is None:
            raise ValueError('if activity is Activity.custom then activity_id must be passed')  # noqa: E501
            return
        return await _create_normal_invite_link(activity_id)


nextcord.VoiceChannel.create_activity_invite = create_activity_invite_link
