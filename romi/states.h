/*
 * states.h
 *
 *  Created on: Sep 22, 2018
 *      Author: shromonaghosh
 */

#ifndef STATES_H_
#define STATES_H_

#include <stdio.h>

typedef enum {
    OFF=0,
  	DRIVING, 
  	TURN_RIGHT,
  	SUBTARGET_REACHED,
  	PAUSE,
  	TURN_LEFT
} states;

#endif /* STATES_H_ */
