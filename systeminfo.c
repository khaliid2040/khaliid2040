#include <stdio.h>
#include <sys/sysinfo.h>
#include <unistd.h>
#include <pwd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/utsname.h>
#include <sys/statvfs.h>

/* some neccessary functions need the program to work*/
typedef unsigned long cpuInfo;
typedef const char* cpuProperty;
typedef unsigned long long d_size;
int getProcessInfo(pid_t pid, unsigned long uptime) {
    char statPath[256];
    snprintf(statPath, sizeof(statPath), "/proc/%d/stat", pid);

    FILE* statFile = fopen(statPath, "r");
    if (statFile == NULL) {
        perror("Failed to open stat file");
        return -1;
    }

    int processId;
    char processName[256];
    cpuInfo utime, stime;
    cpuInfo hertz = sysconf(_SC_CLK_TCK);
    double process_total_time;
    double cpu_percentage;

    fscanf(statFile, "%d (%[^)]) %*c %*d %*d %*d %*d %*d %*u "
                     "%*lu %*lu %*lu %*lu %*lu %lu %lu", &processId, processName, &utime, &stime);

    process_total_time = (double)(utime + stime) / hertz;
    double process_total_time_percent= (process_total_time / uptime) * 100;
    double userspace_time= (process_total_time / utime);
    double system_time= (process_total_time / stime);
    printf("Process ID: %d\n", pid);
    printf("Process Name: %s\n", processName);
    printf("CPU Time: %.2f seconds\n", process_total_time);
    printf("process time percent %.2f %\n", process_total_time_percent);
    printf("user time percent %.2f %\n", userspace_time);
    printf("system time percent %.2f %\n", system_time);
    fclose(statFile);

    return 0;
}
/*system information function*/
void systeminfo( int getpid)
{
    /*using the information provided by sysinfo library data structure*/
    struct sysinfo system_info;
    if (sysinfo(&system_info) == 0)
    {
        unsigned short uptime_min= system_info.uptime / 60;
        printf("uptime %d minutes", uptime_min);
        printf("\nTotal memory: %d GB\n", system_info.totalram / 1024 / 1024 / 1024);
        
    }
    /* since the program is doing system related things for security reasons it must not be run as root
    if next time needed we will remove this code but now it must be their for security reasons */
    __uid_t uid= getuid();
    __gid_t gid= getgid();
    //now getting kernel information
    printf("checking running kernel\n");
    struct utsname kernel_info;
    if (uname(&kernel_info) == -1)
    {
        perror("error");
    }
    printf("kernel version: %s\n",kernel_info.release);
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
    long total_time= system_info.uptime;
    getProcessInfo(getpid, total_time);
    
    /*
        cpuinfo_buffer holds the buffer of the cpuinfo file
        buffer_size is the size of the buffer
        processors and cores are strings searched in  the file
        
    */
    char *cpuinfo_buffer= NULL;
    size_t buffer_size= 0;
    cpuProperty processors = "processor";
    cpuProperty cores = "cores";
    int processors_count= 0;
    int cores_count= 0;
    FILE *cpuinfo = fopen("/proc/cpuinfo","r");

    if (cpuinfo == NULL) {
        printf("Failed to open cpuinfo file.\n");

    }
    while (getline(&cpuinfo_buffer, &buffer_size, cpuinfo) != -1)
    {
        if (strstr(cpuinfo_buffer, processors) != NULL) {
            processors_count++;
        }
        if (strstr(cpuinfo_buffer, cores) != NULL) {
            cores_count++;
        }
    }
    printf("Number of cores: %d\n", cores_count /2);
    printf("number of processors: %d\n",processors_count);
    // checking firmware

    free(cpuinfo_buffer);
    fclose(cpuinfo);
    struct statvfs vfs;
    char* mountpoints[]= {"/", "/boot", "/boot/efi","/home"};
    int mp_count= 5;
    d_size total_blocks,block_size,available_blocks,total_size,available_size;
    double total_gb,available_gb;
    for (int i=0; i <mp_count; i++)
    {
        if (statvfs(mountpoints[i], &vfs)== -1)
        {
            perror("statvfs: error");
            return -1;
        }   
    
        /*in case of size_d it declared in the about typedefs size mean total size and d is short for disk
            so it abbriviated on size_disk*/
        total_blocks= vfs.f_blocks;
        block_size= vfs.f_frsize;
        available_blocks= vfs.f_bavail;
        total_size= block_size * total_blocks;
        available_size= block_size * available_blocks;
        total_gb= (double) total_size / (1024 * 1024 * 1024);
        available_gb= (double) available_size / (1024 * 1024 * 1024);
        printf("total size of mountpoint %s: %.2f GB\n", total_gb,mountpoints[i]);
        printf("available size of mounpoint %s: %.2f GB\n\n", available_gb, mountpoints[i]);
    }
}
int main(int argc, char *argv[])
{
    printf("system enumeration\n");
    
    
    if (argc < 2)
    {
        printf("too few arguments\n");
        return 1;
    } else if (strcmp(argv[1], "-p")== 0)
    {
        int pid = atoi(argv[2]);
        systeminfo(pid);
    } else {
        printf("invalid option\n");
        return 2;
    }
    
    return 0;
}