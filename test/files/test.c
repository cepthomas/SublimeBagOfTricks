/**
 * @file gsib-common.c
 *
 * @brief Common utilities.
 *
 * @copyright 2020 Ceres Innovation, All rights reserved.
 */



/* ======================= INCLUDES ========================================= */

#include "stm32f0xx.h"
#include "gsib_common.h"
#include "can_manager.h"


/* ======================= PRIVATE ========================================== */


//#region Stuff

static int p_iiiii;

/* ======================= PUBLIC FUNCTION IMPLEMENTATIONS ================== */

//#region Nested

void common_uint32ToBytes(uint32_t val, uint8_t* bytes, bool lend)
{
    if(lend)
    {
        /* comment */
        bytes[0] = (val) & 0xFF;
        bytes[1] = (val >> 8) & 0xFF;
        bytes[2] = (val >> 16) & 0xFF;
        bytes[3] = (val >> 24) & 0xFF;
    }
    else
    {
        bytes[3] = (val) & 0xFF;
        bytes[2] = (val >> 8) & 0xFF;
        bytes[1] = (val >> 16) & 0xFF;
        bytes[0] = (val >> 24) & 0xFF;
    }
}

//#endregion

/* -------------------------------------------------------------------------- */

void common_bytesToUint32(uint8_t bytes[], uint32_t* val, bool lend)
{
    if(lend)
    {
        *val = ((uint32_t)bytes[0]) | ((uint32_t)bytes[1] << 8) | ((uint32_t)bytes[2] << 16) | ((uint32_t)bytes[3] << 24);
    }
    else
    {
        *val = ((uint32_t)bytes[3]) | ((uint32_t)bytes[2] << 8) | ((uint32_t)bytes[1] << 16) | ((uint32_t)bytes[0] << 24);
    }
}

/* -------------------------------------------------------------------------- */

bool atoi_ex(char* string, int32_t* val)
{
    bool ok = true;
    *val = 0;

    uint8_t digit = 0;
    bool negative = false;

    // Skip any leading blanks.
    while(' ' == *string)
    {
        string += 1;
    }

    // Check for a sign.
    if (*string == '-')
    {
        negative = true;
        string += 1;
    }
    else
    {
        if (*string == '+')
        {
            string += 1;
        }
    }

    bool done = false;
    for ( ; ok == true && done == false; string += 1)
    {
        if(*string == 0)
        {
            done = true;
        }
        else
        {
            digit = *string - '0';
            if (digit >= 0 && digit <= 9)
            {
                *val = (10 * (*val)) + digit;
            }
            else
            {
                done = true;
                ok = false;
            }
        }
    }

    if(negative)
    {
        *val = -*val;
    }

    return ok;
}

/* -------------------------------------------------------------------------- */

bool common_sendTrace(uint8_t msgid, const char* text, uint32_t val)
{
    // Send the text.
    can_status_t cstat = canManager_sendTrace(msgid, text);

    // Send a string version of val.
    char buff[8];
    for(uint8_t i = 0; i < 8; i++)
    {
        uint8_t byte = (val >> i * 4) & 0x0000000F;

        if(byte >= 0 && byte <= 9)
        {
            buff[7-i] = byte + '0';
        }
        else if(byte >= 10 && byte <= 15)
        {
            buff[7-i] = (byte - 10) + 'A';
        }
        else
        {
            buff[7-i] = '?';
        }
    }
    cstat = canManager_sendTrace(msgid, buff);

    return CAN_OK == cstat;
}

//#endregion
