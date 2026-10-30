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

// FILE: SupplySourceUpdate.cpp ///////////////////////////////////////////////////////////////////
// Desc:   Reloads empty RESUPPLY weapons of allied objects within a radius
///////////////////////////////////////////////////////////////////////////////////////////////////

#include "PreRTS.h"	// This must go first in EVERY cpp file in the GameEngine

#include "Common/Xfer.h"
#include "GameLogic/Module/SupplySourceUpdate.h"
#include "GameLogic/Object.h"
#include "GameLogic/PartitionManager.h"
#include "GameLogic/Weapon.h"

//-------------------------------------------------------------------------------------------------
SupplySourceUpdate::SupplySourceUpdate( Thing *thing, const ModuleData* moduleData ) : UpdateModule( thing, moduleData )
{
	setWakeFrame(getObject(), UPDATE_SLEEP(getSupplySourceUpdateModuleData()->m_scanDelay));
}

//-------------------------------------------------------------------------------------------------
SupplySourceUpdate::~SupplySourceUpdate()
{
}

//-------------------------------------------------------------------------------------------------
static void resupplyObject(Object *obj)
{
	for (Int slot = PRIMARY_WEAPON; slot < WEAPONSLOT_COUNT; ++slot)
	{
		Weapon *weapon = obj->getWeaponInWeaponSlot((WeaponSlotType)slot);
		if (weapon && weapon->getReloadType() == RESUPPLY_TO_RELOAD && weapon->getStatus() == OUT_OF_AMMO)
		{
			weapon->reloadAmmo(obj);
		}
	}
}

//-------------------------------------------------------------------------------------------------
UpdateSleepTime SupplySourceUpdate::update()
{
	const SupplySourceUpdateModuleData *d = getSupplySourceUpdateModuleData();
	Object *self = getObject();

	if (!self->isEffectivelyDead() && !self->isDisabled() && !self->testStatus(OBJECT_STATUS_UNDER_CONSTRUCTION))
	{
		PartitionFilterRelationship relationship( self, PartitionFilterRelationship::ALLOW_ALLIES );
		PartitionFilterSameMapStatus filterMapStatus( self );
		PartitionFilterAlive filterAlive;
		PartitionFilter *filters[] = { &relationship, &filterAlive, &filterMapStatus, nullptr };

		ObjectIterator *iter = ThePartitionManager->iterateObjectsInRange( self->getPosition(), d->m_supplyRadius, FROM_CENTER_2D, filters );
		MemoryPoolObjectHolder hold( iter );
		for (Object *other = iter->first(); other; other = iter->next())
		{
			resupplyObject(other);
		}
	}

	return UPDATE_SLEEP(d->m_scanDelay);
}

// ------------------------------------------------------------------------------------------------
/** CRC */
// ------------------------------------------------------------------------------------------------
void SupplySourceUpdate::crc( Xfer *xfer )
{
	UpdateModule::crc( xfer );
}

// ------------------------------------------------------------------------------------------------
/** Xfer method
	* Version Info:
	* 1: Initial version */
// ------------------------------------------------------------------------------------------------
void SupplySourceUpdate::xfer( Xfer *xfer )
{
	XferVersion currentVersion = 1;
	XferVersion version = currentVersion;
	xfer->xferVersion( &version, currentVersion );

	UpdateModule::xfer( xfer );
}

// ------------------------------------------------------------------------------------------------
/** Load post process */
// ------------------------------------------------------------------------------------------------
void SupplySourceUpdate::loadPostProcess()
{
	UpdateModule::loadPostProcess();
}
