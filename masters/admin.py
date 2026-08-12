from django.contrib import admin

from .models import Customer, Furnace, Machine, Product, Shift, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "gstin", "phone", "active")
    list_filter = ("active",)
    search_fields = ("code", "name", "gstin")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "gstin", "phone", "active")
    list_filter = ("active",)
    search_fields = ("code", "name", "gstin")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "drawing_no", "material_spec", "active")
    list_filter = ("active",)
    search_fields = ("code", "name", "drawing_no")


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "machine_type", "location", "active")
    list_filter = ("machine_type", "active")
    search_fields = ("code", "name")


@admin.register(Furnace)
class FurnaceAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "furnace_type", "capacity", "active")
    list_filter = ("active",)
    search_fields = ("code", "name")


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "active")
    list_filter = ("active",)
