echo
echo "Git clone started."
echo
git clone "https://github.com/jetsonhacks/rootOnNVMe"
echo "Git clone is done."
echo
cd   "rootOnNVMe"
echo "changed directory to rootONVMe"
echo

sh "./copy-rootfs-ssd.sh"
echo " to "
sh "./setup-service.sh"
echo "completed"
