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

// FILE: SupplySourceUpdate.h /////////////////////////////////////////////////////////////////////
// Desc:   Reloads empty RESUPPLY weapons of allied objects within a radius
///////////////////////////////////////////////////////////////////////////////////////////////////

#pragma once

#include "GameLogic/Module/UpdateModule.h"

//-------------------------------------------------------------------------------------------------
class SupplySourceUpdateModuleData : public UpdateModuleData
{
public:
	Real m_supplyRadius;
	UnsignedInt m_scanDelay;

	SupplySourceUpdateModuleData()
	{
		m_supplyRadius = 0.0f;
		m_scanDelay = LOGICFRAMES_PER_SECOND;
	}

	static void buildFieldParse(MultiIniFieldParse& p)
	{
		UpdateModuleData::buildFieldParse(p);
		static const FieldParse dataFieldParse[] =
		{
			{ "SupplyRadius",	INI::parseReal,									nullptr, offsetof( SupplySourceUpdateModuleData, m_supplyRadius ) },
			{ "ScanDelay",		INI::parseDurationUnsignedInt,	nullptr, offsetof( SupplySourceUpdateModuleData, m_scanDelay ) },
			{ nullptr, nullptr, nullptr, 0 }
		};
		p.add(dataFieldParse);
	}
};

//-------------------------------------------------------------------------------------------------
class SupplySourceUpdate : public UpdateModule
{
	MEMORY_POOL_GLUE_WITH_USERLOOKUP_CREATE( SupplySourceUpdate, "SupplySourceUpdate" )
	MAKE_STANDARD_MODULE_MACRO_WITH_MODULE_DATA( SupplySourceUpdate, SupplySourceUpdateModuleData )

public:
	SupplySourceUpdate( Thing *thing, const ModuleData* moduleData );
	// virtual destructor prototype provided by memory pool declaration

	virtual UpdateSleepTime update() override;
};
