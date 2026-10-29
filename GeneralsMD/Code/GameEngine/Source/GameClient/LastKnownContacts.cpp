/*
**	Command & Conquer Generals Zero Hour(tm)
**	Copyright 2025 Electronic Arts Inc.
**
**	This program is free software: you can redistribute it and/or modify
**	it under the terms of the GNU General Public License as published by
**	the Free Software Foundation, either version 3 of the License, or
**	(at your option) any later version.
**
**	This program is distributed in the hope that it will be useful,
**	but WITHOUT ANY WARRANTY; without even the implied warranty of
**	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
**	GNU General Public License for more details.
**
**	You should have received a copy of the GNU General Public License
**	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

// FILE: LastKnownContacts.cpp ////////////////////////////////////////////////////////////////////

#include "PreRTS.h"	// This must go first in EVERY cpp file in the GameEngine

#include "GameClient/LastKnownContacts.h"

#include "Common/GameUtility.h"
#include "Common/GlobalData.h"
#include "Common/Player.h"
#include "GameClient/Color.h"
#include "GameClient/Display.h"
#include "GameClient/View.h"
#include "GameLogic/GameLogic.h"
#include "GameLogic/Object.h"
#include "GameLogic/PartitionManager.h"

static UnsignedInt getContactDurationFrames()
{
	return REAL_TO_UNSIGNEDINT(TheGlobalData->m_lastKnownContactDuration * LOGICFRAMES_PER_SECOND);
}

Bool LastKnownContacts::isTracked(const Object *object)
{
	if (object->isKindOf(KINDOF_IMMOBILE) || object->isEffectivelyDead())
		return false;

	if (!object->isKindOf(KINDOF_VEHICLE) && !object->isKindOf(KINDOF_INFANTRY) && !object->isKindOf(KINDOF_AIRCRAFT))
		return false;

	const Player *localPlayer = rts::getObservedOrLocalPlayer();
	return localPlayer && localPlayer->getRelationship(object->getTeam()) == ENEMIES;
}

void LastKnownContacts::remove(ObjectID objectID)
{
	for (size_t i = 0; i < m_contacts.size(); ++i)
	{
		if (m_contacts[i].objectID == objectID)
		{
			m_contacts[i] = m_contacts.back();
			m_contacts.pop_back();
			return;
		}
	}
}

void LastKnownContacts::onObscuredChanged(const Object *object, Bool obscured)
{
	if (getContactDurationFrames() == 0)
		return;

	remove(object->getID());

	if (!obscured || !isTracked(object))
		return;

	const Player *owner = object->getControllingPlayer();

	Contact contact;
	contact.objectID = object->getID();
	contact.position = *object->getPosition();
	contact.color = owner ? owner->getPlayerColor() : GameMakeColor(255, 255, 255, 255);
	contact.lostFrame = TheGameLogic->getFrame();
	m_contacts.push_back(contact);
}

void LastKnownContacts::update()
{
	const UnsignedInt duration = getContactDurationFrames();
	const UnsignedInt now = TheGameLogic->getFrame();
	const Int localPlayerIndex = rts::getObservedOrLocalPlayerIndex_Safe();

	for (size_t i = 0; i < m_contacts.size(); )
	{
		const Contact &contact = m_contacts[i];
		const Bool expired = now - contact.lostFrame >= duration;
		const Bool seenAgain = ThePartitionManager->getShroudStatusForPlayer(localPlayerIndex, &contact.position) == CELLSHROUD_CLEAR;

		if (expired || seenAgain)
		{
			m_contacts[i] = m_contacts.back();
			m_contacts.pop_back();
		}
		else
		{
			++i;
		}
	}
}

void LastKnownContacts::draw()
{
	const UnsignedInt duration = getContactDurationFrames();
	if (duration == 0 || !TheTacticalView)
		return;

	const UnsignedInt now = TheGameLogic->getFrame();
	const Int halfSize = 6;

	for (size_t i = 0; i < m_contacts.size(); ++i)
	{
		const Contact &contact = m_contacts[i];

		ICoord2D screen;
		if (!TheTacticalView->worldToScreen(&contact.position, &screen))
			continue;

		// Fade from fully opaque to a faint marker as the information ages.
		const Real age = (Real)(now - contact.lostFrame) / (Real)duration;
		const UnsignedByte alpha = (UnsignedByte)REAL_TO_INT(255.0f - 195.0f * std::min(age, 1.0f));

		UnsignedByte r, g, b, a;
		GameGetColorComponents(contact.color, &r, &g, &b, &a);
		const Color color = GameMakeColor(r, g, b, alpha);

		TheDisplay->drawLine(screen.x - halfSize, screen.y, screen.x, screen.y - halfSize, 2.0f, color);
		TheDisplay->drawLine(screen.x, screen.y - halfSize, screen.x + halfSize, screen.y, 2.0f, color);
		TheDisplay->drawLine(screen.x + halfSize, screen.y, screen.x, screen.y + halfSize, 2.0f, color);
		TheDisplay->drawLine(screen.x, screen.y + halfSize, screen.x - halfSize, screen.y, 2.0f, color);
	}
}

void LastKnownContacts::reset()
{
	m_contacts.clear();
}
