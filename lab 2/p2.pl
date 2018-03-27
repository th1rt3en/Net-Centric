my @list;
my $len;
my $buffer;
print "number of strings: ";
$len = <stdin>;
while ($len-- > 0) {
	$buffer = <stdin>;
	push @list, $buffer;
}
while (@list){
	$buffer = pop @list;
	print join '', map substr($buffer, -$_, 1), 1..length($buffer);
}
print "\n";

