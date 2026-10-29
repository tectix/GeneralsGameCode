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

// FILE: LastKnownContacts.h //////////////////////////////////////////////////////////////////////
// Remembers where enemy units were last seen by the local player after they disappear into the
// fog of war, and draws a fading marker there until the information expires or the spot is seen
// again.
///////////////////////////////////////////////////////////////////////////////////////////////////

#pragma once

#include "Common/GameCommon.h"
#include "GameClient/Color.h"

class Object;

class LastKnownContacts
{
public:
	void onObscuredChanged(const Object *object, Bool obscured); ///< Call when an object's fog state changes for the local player.
	void update();
	void draw();
	void reset();

private:
	struct Contact
	{
		ObjectID objectID;
		Coord3D position;
		Color color;
		UnsignedInt lostFrame;
	};

	static Bool isTracked(const Object *object);
	void remove(ObjectID objectID);

	std::vector<Contact> m_contacts;
};
