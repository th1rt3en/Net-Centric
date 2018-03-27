use IO::Socket;

$socket = new IO::Socket::INET (
                                  PeerAddr  => '127.0.0.1',
                                  PeerPort  =>  2121,
                                  Proto => 'tcp',
                               )                
or die "Couldn't connect to Server\n";

while (1){

	$data;
	$socket->recv($data, 1024);
	
	print $data;
		
	$data = <STDIN>;
	chop($data);
	$socket->send($data);

	while (1) {
		$socket->recv($data, 1024);
		if ($data eq "eof"){ 
			close($socket);
			last; 
		}
		print $data;
	}
	last;
}
