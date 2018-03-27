use IO::Socket;

$socket = new IO::Socket::INET (
                                  PeerAddr  => '127.0.0.1',
                                  PeerPort  =>  9999,
                                  Proto => 'tcp',
                               )                
or die "Couldn't connect to Server\n";

while (1){

	$data = <STDIN>;
	chop($data);
	$socket->send($data);

	if ($data eq "exit"){ 
		close($socket);
		last; 
	}

	$socket->recv($data, 1024);
	print $data;
		
}
	
