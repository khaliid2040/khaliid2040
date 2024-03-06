#include <stdio.h>
#include <sys/sysinfo.h>
#include <unistd.h>
#include <pwd.h>
#include <stdlib.h>
#include <string.h>
/* some neccessary functions need the program to work*/
int getProcessInfo(pid_t pid, char *buffer, size_t bufferSize) {
    char path[32];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        return -1;
    }
    
    int scanned = fscanf(file, "%*d (%[^)])", buffer);
    fclose(file);
    
    if (scanned == 1) {
        return 0;
    } else {
        return -1;
    }
    char statPath[256];
    char statmPath[256];
    snprintf(statPath, sizeof(statPath), "/proc/%s/stat", pid);
    snprintf(statmPath, sizeof(statmPath), "/proc/%s/statm", pid);

    FILE* statFile = fopen(statPath, "r");
    FILE* statmFile = fopen(statmPath, "r");

    if (statFile && statmFile) {
        int processId;
        char processName[256];
        unsigned long utime, stime;
        unsigned long rss;

        fscanf(statFile, "%d (%[^)]) %*c %*d %*d %*d %*d %*d %*u "
                         "%*lu %*lu %*lu %*lu %*lu %lu %lu", &processId, processName, &utime, &stime);
        fscanf(statmFile, "%*lu %lu", &rss);

        printf("Process ID: %d\n", pid);
        printf("Process Name: %s\n", processName);
        printf("CPU Time (user): %lu\n", utime);
        printf("CPU Time (system): %lu\n", stime);
        printf("Resident Set Size (RSS): %lu\n\n", rss);

        fclose(statFile);
        fclose(statmFile);
    }
}
/*system information function*/
void systeminfo( int getpid)
{
    /*using the information provided by sysinfo library data structure*/
    struct sysinfo system_info;
    if (sysinfo(&system_info) == 0)
    {
        printf("uptime: %ld", system_info.uptime);
        printf("\nTotal memory: %d GB\n", system_info.totalram / 1024 / 1024);
        
    }
    /* since the program is doing system related things for security reasons it must not be run as root
    if next time needed we will remove this code but now it must be their for security reasons */
    __uid_t uid= getuid();
    __gid_t gid= getgid();
    
    printf("Warning: this script wan't supposed to be run under the root user \n");
    if (uid < 1000 && gid < 1000)
    {
        printf("the program doesn't allowed to be run under this users\n");
        _exit(2);
    } else {
        char *username= getlogin();
        printf("checking users up to 2000\n");
        for (int i=0; i < 2000; i++)
        {
            struct passwd *pw= getpwuid(i);
            if (i<1000 && i !=0)
            {
                continue;
            } else
            {
                if (pw !=NULL)
                {
                    printf("user %s exist\n", pw->pw_name);
                }
            }
        }
    }
    printf("getting process information\n");
    char buffer[255];
    getProcessInfo(getpid,buffer, sizeof(buffer));
    printf("%s\n",buffer);
    /*
        cpuinfo_buffer holds the buffer of the cpuinfo file
        buffer_size is the size of the buffer
        processors and cores are strings searched in  the file
        
    */
    char *cpuinfo_buffer= NULL;
    size_t buffer_size= 0;
    const char* processors = "processor";
    const char* cores = "cores";
    int processors_count= 0;
    int cores_count= 0;
    FILE *cpuinfo = fopen("/proc/cpuinfo","r");
    while (getline(&cpuinfo_buffer, &buffer_size, cpuinfo) != -1)
    {
        if (strstr(cpuinfo_buffer, processors) != NULL) {
            processors_count++;
            
        }
        if (strstr(cpuinfo_buffer, cores) != NULL) {
            cores_count++;
            printf("%s", cpuinfo_buffer);
            break;
        }
    }
    printf("number of processors: %d\n",processors_count);
    
    free(cpuinfo_buffer);
    fclose(cpuinfo);
}
int main()
{
    printf("system enumeration\n");
    
    __pid_t pid;
    printf("enter process ID: ");
    scanf("%d",&pid);
    systeminfo(pid);
    return 0;
}