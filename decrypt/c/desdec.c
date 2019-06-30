/*
 *  desdec.c
 *  https://github.com/sam210723/COMS-1
 */

#include <stdio.h>
#include <string.h>

/*
 *  Prints help text to the console
 */
void help()
{
    puts("DES Decryption Utility (single-layer only)\n");
    
    puts("desdec [INPUT] [OUTPUT] [KEY]");
    puts("  [INPUT]:    Encrypted input file path");
    puts("  [OUTPUT]:   Decrypted output file path");
    puts("  [KEY]:      8-byte DES key");
}


int main(int argc, char *argv[])
{
    // Show help text if missing arguments
    if (argc < 4)
    {
        help();
    }

    // Loop through arguments
    for (int i = 1; i < argc; i++)
    {
        
    }
}
