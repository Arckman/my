# Read from the file file.txt and output all valid phone numbers to stdout.
sed -n '{
    /^([0-9][0-9][0-9]) [0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]$/p
    /^[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]$/p
    }' file.txt


sed -n -r '{
    /^\([0-9]{3}\) [0-9]{3}-[0-9]{4}$/p
    /^[0-9]{3}-[0-9]{3}-[0-9]{4}$/p
    }' file.txt