use IO::Socket;

$| = 1;

$socket = new IO::Socket::INET (
	LocalHost => '127.0.0.1',
	LocalPort => '2121',
	Proto => 'tcp',
	Listen => 5,
	Reuse => 1
) or die "Coudn't open socket\n";

print "TCPServer Waiting for client on port 2121\n";

while(1){

	$client_socket = "";
	$client_socket = $socket->accept();
	
	$peer_address = $client_socket->peerhost();
	$peer_port = $client_socket->peerport();
	
	print "Connection from ($peer_address, $peer_port)\n";

	$client_socket->send("Enter filename: ");	

	$client_socket->recv($name, 1024);

	if (open(my $fh, '<:encoding(UTF-8)', "$name.txt")) {
		while (my $row = <$fh>) {
  			chomp $row;
			$client_socket->send("$row\n");
		}
	} else {
		warn "File not found\n";
		$client_socket->send("No such file\n");
	}
	$client_socket->send("eof");
	close $client_socket;
	last;
	
}
