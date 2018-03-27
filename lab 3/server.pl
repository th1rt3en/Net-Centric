use IO::Socket;

$| = 1;

$socket = new IO::Socket::INET (
	LocalHost => '127.0.0.1',
	LocalPort => '9999',
	Proto => 'tcp',
	Listen => 5,
	Reuse => 1
) or die "Coudn't open socket\n";

print "TCPServer Waiting for client on port 9999\n";

while(1){

	$client_socket = "";
	$client_socket = $socket->accept();
	
	$peer_address = $client_socket->peerhost();
	$peer_port = $client_socket->peerport();
	
	print "Connection from ($peer_address, $peer_port)\n";
	
	$value = int(rand(101));
	$min = 0;
	$max = 100;
	
	while (1) {
	
		$client_socket->send("Enter a number in range $min - $max\n");
		$client_socket->recv($guess, 1024);
		
		print "Client guessed $guess\n";
		
		if ($guess > $value){ $max = $guess; }
		elsif ($guess < $value){ $min = $guess; }
		else { last; }
	}
	
	$client_socket->send("You have guessed correctly\n");
	close $client_socket;
	last;
	
}
