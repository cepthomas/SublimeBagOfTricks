/**
 * @file test.c
 */



/* ======================= INCLUDES ========================================= */

#include "stm32f0xx.h"
#include "gsib_common.h"
#include "can_manager.h"




/* ======================= PUBLIC FUNCTION IMPLEMENTATIONS ================== */

void common_uint32ToBytes(uint32_t val, uint8_t* bytes, bool lend){
    if(lend)    {
    bytes[0] = (val) & 0xFF; /*

c style comment
*/    

    bytes[1] = (val >> 8) & 0xFF;
    bytes[2] = (val >> 16) & 0xFF;
    bytes[3] = (val >> 24) & 0xFF;
}    else
    {
// commentsssssssssss        
        bytes[3] = (val) & 0xFF;
        bytes[2] = (val >> 8) & 0xFF;
        bytes[1] = (val >> 16) & 0xFF;
        bytes[0] = (val >> 24) & 0xFF;
    }
}

/* -------------------------------------------------------------------------- */

void common_bytesToUint32(uint8_t bytes[], uint32_t* val, bool lend)
{
    if(lend)    {        *val = ((uint32_t)bytes[0]) | ((uint32_t)bytes[1] << 8) | ((uint32_t)bytes[2] << 16) | ((uint32_t)bytes[3] << 24);    }
else
{
*val = ((uint32_t)bytes[3]) | ((uint32_t)bytes[2] << 8) | ((uint32_t)bytes[1] << 16) | ((uint32_t)bytes[0] << 24);
}
}
