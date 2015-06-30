#!/bin/sh

ct=1

while [ $ct -lt 20 ]
do
   echo $ct
   net='net'$ct
   neutron net-create $net
   cidr=$ct'.0.0.0/24'
   neutron subnet-create $net $cidr
   prt=1
   while [ $prt -lt 30 ]
   do
       neutron port-create $net
       prt=`expr $prt + 1`
   done
   ct=`expr $ct + 1`
done
