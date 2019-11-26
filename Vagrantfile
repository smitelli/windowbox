Vagrant.configure("2") do |config|
  config.vm.box = "debian/contrib-buster64"
  config.vm.post_up_message = nil

  config.vm.provider "virtualbox" do |vb|
    vb.cpus = 1
    vb.memory = 1024
  end

  config.vm.hostname = "dev-windowbox"
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  config.vm.provision "shell", privileged: false, inline: <<~EOF
    VARDIR=/var/opt/windowbox

    sudo DEBIAN_FRONTEND=noninteractive apt-get -yq update
    sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install libimage-exiftool-perl virtualenv

    sudo install -o vagrant -g vagrant -m 755 -d $VARDIR
    virtualenv -p /usr/bin/python3 $VARDIR/.virtualenv
    $VARDIR/.virtualenv/bin/pip install -e /vagrant[dev]

    grep PROVISION_DONE $HOME/.profile > /dev/null || (
      echo >> $HOME/.profile
      echo "PATH=\\"$VARDIR/.virtualenv/bin:\\$PATH\\"" >> $HOME/.profile
      echo "cd /vagrant" >> $HOME/.profile
      echo "# PROVISION_DONE" >> $HOME/.profile
    )
  EOF
end
