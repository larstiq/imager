# -*-mic2-options-*- --arch=i586 -*-mic2-options-*-
# 
# Do not Edit! Generated by:
# kickstarter.py
# 

lang en_US.UTF-8
keyboard us
timezone --utc UTC
part / --size 500 --ondisk sda --fstype=ext4
rootpw rootme 

user --name mer  --groups audio,video --password rootme 

repo --name=mer-core --baseurl=http://releases.merproject.org/releases/latest/builds/i586/packages/
repo --name=mer-tools --baseurl=http://repo.pub.meego.com//Mer:/Tools:/Testing/Mer_Core_i586/ 
repo --name=vm-kernel --baseurl=http://repo.pub.meego.com//home:/iamer:/Mer:/SDK/Mer_Core_i586/


%packages --excludedocs

@Mer Core

openssh-server
net-tools
kernel-adaptation-vm
mic

%end

%post

%end

%post --nochroot

%end
