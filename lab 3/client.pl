use IO::Socket;

$socket = new IO::Socket::INET (
                                  PeerAddr  => '127.0.0.1',
                                  PeerPort  =>  9999,
                                  Proto => 'tcp',
                               )                
or die "Couldn't connect to Server\n";

while (1){

	$data;
	$socket->recv($data, 1024);
	
	print $data;
		
	if ($data eq "You have guessed correctly\n"){ 
		close($socket);
		last; 
	}		

	$data = <STDIN>;
	chop($data);
	$socket->send($data);
	
}
	
