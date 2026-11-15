// D2R's "is HD graphics on" query (a function of D2R's image 0x6ab3782c), the one entry of D2R-XL 2012's
// rotw_stash_logic.h that panel_shared.cpp uses.
#pragma once

#include <cstdint>

namespace rotw_stash {
inline constexpr uint64_t HdModeRva = 0x846210;
}  // namespace rotw_stash
