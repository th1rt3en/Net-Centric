my $buffer;
my @array;
$buffer = <stdin>;
while ($buffer != 999) {
	push @array, $buffer;
	$buffer = <stdin>;
}
print eval join '+', @array;
print "\n";
