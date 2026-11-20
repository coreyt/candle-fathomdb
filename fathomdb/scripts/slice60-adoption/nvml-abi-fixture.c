#include <nvml.h>
#include <stddef.h>
#include <stdio.h>
int main(void) {
    nvmlProcessInfo_t a[2] = {{101, 1001, 11, 12}, {202, 2002, 21, 22}};
    fprintf(stderr, "sizeof=%zu pid=%zu used=%zu gpu=%zu compute=%zu\n", sizeof(a[0]), offsetof(nvmlProcessInfo_t,pid), offsetof(nvmlProcessInfo_t,usedGpuMemory), offsetof(nvmlProcessInfo_t,gpuInstanceId), offsetof(nvmlProcessInfo_t,computeInstanceId));
    return fwrite(a, sizeof(a), 1, stdout) == 1 ? 0 : 1;
}
