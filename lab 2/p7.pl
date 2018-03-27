my @array;
my $buffer;
print "number of string:";
my $len = <stdin>;
while ($len-- > 0) {
	$buffer = <stdin>;
	push @array, $buffer;
}
sub remove_dup {
	%seen = ();
	@array = grep { ! $seen{$_} ++ } @array;
	print join ' ', @array, "\n";
}
sub sort {
	@array = sort {lc($a) cmp lc($b)} @array;
	print join ' ', @array, "\n";
}
sub index_of {
	my ($str) = @_;
	my ($index) = grep { $array[$_] eq $str } (0 .. @array-1);
    return $index;
}
sub replace {
	my ($s1, $s2) = @_;
	$array[index_of($s1)] = $s2;
	print join ' ', @array, "\n";
}
sub remove {
	my ($index) = @_;
	splice(@array,$index,1);
	print join ' ', @array, "\n";
}
sub move {
	my ($str) = @_;
	unshift(@array, splice(@array, index_of($str), 1));
	print join ' ', @array, "\n";
}
sub p {
	my @a = @_;
	print @a;
}
p(@a);

