use IO::Socket;

$socket = new IO::Socket::INET (
                                  PeerAddr  => '127.0.0.1',
                                  PeerPort  =>  9998,
                                  Proto => 'tcp',
                               )                
or die "Couldn't connect to Server\n";

while (1){	

	$socket->recv($msg, 1024);

	if ($msg eq "mv" or $msg eq "sh"){
		$cmd = <STDIN>;
		chomp $cmd;
		$socket->send($cmd);
	} else {
		print $msg;
	}
}
