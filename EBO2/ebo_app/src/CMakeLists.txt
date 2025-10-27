cmake_minimum_required(VERSION 2.6)
PROJECT(  ebo_app )

INCLUDE( /home/robocomp/robocomp/cmake/robocomp.cmake )

ROBOCOMP_IDSL_TO_ICE( CommonBehavior DifferentialRobot EboASR EboMoods EmotionalMotor GPT GenericBase LEDArray Speech )
